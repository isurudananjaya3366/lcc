# File Upload Patterns

> Common patterns for implementing file uploads in the LankaCommerce Cloud
> platform. Choose the pattern that best fits your use case.

---

## Pattern 1: Direct Upload (HTML Form)

**Use Case:** Simple file upload via standard HTML form submission.

**Flow:**

1. User selects file → 2. Form POST → 3. Server validates →
2. Server saves to storage → 5. DB record created → 6. Response/redirect

### Django View

```python
from django.http import JsonResponse
from django.views import View
from apps.core.storage import TenantFileStorage, FileValidator, get_image_validator

class FileUploadView(View):
    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file provided"}, status=400)

        # Validate
        validator = get_image_validator()
        try:
            validator.validate_all(uploaded_file)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Save
        storage = TenantFileStorage()
        path = storage.save(f"uploads/{uploaded_file.name}", uploaded_file)

        return JsonResponse({
            "url": storage.url(path),
            "filename": uploaded_file.name,
        })
```

### HTML Form

```html
<form method="post" enctype="multipart/form-data" action="{% url 'upload-file' %}">
  {% csrf_token %}
  <input type="file" name="file" required />
  <button type="submit">Upload</button>
</form>
```

**Pros:** Simple, no JavaScript required, works everywhere.
**Cons:** Full page reload, no progress indicator, blocks the UI.

---

## Pattern 2: AJAX Upload with Progress

**Use Case:** Modern web apps needing upload progress and no page reload.

**Flow:**

1. User selects file → 2. JS sends via XHR/fetch → 3. Progress events update UI →
2. Server validates & processes → 5. JSON response updates page

### DRF View

```python
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status

from apps.core.storage import (
    TenantFileStorage, FileValidator, handle_image_upload,
    get_image_validator, product_path,
)


class ImageUploadAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded_file = request.FILES.get("image")
        if not uploaded_file:
            return Response(
                {"error": "No file provided"},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        # Validate
        validator = get_image_validator()
        try:
            validator.validate_all(uploaded_file)
        except ValidationError as e:
            return Response({"error": str(e)}, status=http_status.HTTP_400_BAD_REQUEST)

        # Process (auto sync/async based on size)
        result = handle_image_upload(uploaded_file, instance=None)

        # Save
        storage = TenantFileStorage()
        path = storage.save(f"products/{uploaded_file.name}", result or uploaded_file)

        return Response({
            "url": storage.url(path),
            "filename": uploaded_file.name,
            "size": uploaded_file.size,
        })
```

### JavaScript (XHR with progress)

```javascript
function uploadFile() {
  const fileInput = document.getElementById("file-input");
  const file = fileInput.files[0];
  if (!file) return alert("Please select a file");

  const formData = new FormData();
  formData.append("image", file);

  const xhr = new XMLHttpRequest();

  // Progress
  xhr.upload.addEventListener("progress", (e) => {
    if (e.lengthComputable) {
      const pct = Math.round((e.loaded / e.total) * 100);
      document.getElementById("progress-bar").style.width = pct + "%";
      document.getElementById("progress-text").textContent = pct + "%";
    }
  });

  // Success
  xhr.addEventListener("load", () => {
    if (xhr.status >= 200 && xhr.status < 300) {
      const data = JSON.parse(xhr.responseText);
      document.getElementById("status").textContent = "Upload complete!";
      document.getElementById("preview").src = data.url;
    } else {
      document.getElementById("status").textContent = "Upload failed";
    }
  });

  // Error
  xhr.addEventListener("error", () => {
    document.getElementById("status").textContent = "Network error";
  });

  xhr.open("POST", "/api/upload-image/");
  xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
  xhr.send(formData);
}

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : "";
}
```

### HTML

```html
<input type="file" id="file-input" accept="image/*" />
<button onclick="uploadFile()">Upload</button>
<div class="progress">
  <div id="progress-bar" style="width:0%; height:4px; background:#4caf50;"></div>
</div>
<span id="progress-text"></span>
<div id="status"></div>
<img id="preview" style="max-width:300px; display:none;" />
```

**Pros:** No page reload, real-time progress, better UX.
**Cons:** Requires JavaScript, slightly more complex.

---

## Pattern 3: Large File Multipart/Chunked Upload

**Use Case:** Files > 50 MB that need resume capability and chunked transfer.

**Flow:**

1. JS splits file into chunks → 2. Each chunk sent separately →
2. Server tracks received chunks → 4. Assembles final file →
3. Validates & stores → 6. Cleans up temp chunks

### JavaScript (Chunked Upload)

```javascript
const CHUNK_SIZE = 2 * 1024 * 1024; // 2 MB

async function uploadChunked(file) {
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const uploadId = crypto.randomUUID();

  for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);

    const formData = new FormData();
    formData.append("chunk", chunk);
    formData.append("chunk_number", i + 1);
    formData.append("total_chunks", totalChunks);
    formData.append("upload_id", uploadId);
    formData.append("filename", file.name);

    const resp = await fetch("/api/upload/chunk/", {
      method: "POST",
      headers: { "X-CSRFToken": getCsrfToken() },
      body: formData,
    });

    if (!resp.ok) throw new Error(`Chunk ${i + 1} failed`);

    const data = await resp.json();
    const pct = Math.round(((i + 1) / totalChunks) * 100);
    document.getElementById("progress-text").textContent = `${pct}%`;

    // Last chunk returns the final URL
    if (data.url) {
      console.log("Upload complete:", data.url);
    }
  }
}
```

### Django View (Chunk Receiver)

```python
import os, shutil
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.storage import TenantFileStorage


class ChunkUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        chunk = request.FILES["chunk"]
        chunk_number = int(request.data["chunk_number"])
        total_chunks = int(request.data["total_chunks"])
        upload_id = request.data["upload_id"]
        filename = request.data["filename"]

        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_chunks", upload_id)
        os.makedirs(temp_dir, exist_ok=True)

        # Save this chunk
        chunk_path = os.path.join(temp_dir, f"chunk_{chunk_number:05d}")
        with open(chunk_path, "wb") as f:
            for part in chunk.chunks():
                f.write(part)

        # If all chunks received, assemble
        received = len(os.listdir(temp_dir))
        if received == total_chunks:
            storage = TenantFileStorage()
            from django.core.files.base import ContentFile
            import io

            buffer = io.BytesIO()
            for i in range(1, total_chunks + 1):
                with open(os.path.join(temp_dir, f"chunk_{i:05d}"), "rb") as cf:
                    buffer.write(cf.read())

            buffer.seek(0)
            path = storage.save(f"uploads/{filename}", ContentFile(buffer.read()))
            shutil.rmtree(temp_dir, ignore_errors=True)

            return Response({"url": storage.url(path), "filename": filename})

        return Response({"status": "chunk_received", "received": received})
```

**Pros:** Handles very large files, resumable, reliable on flaky networks.
**Cons:** Complex server-side assembly, temp storage needed, more endpoints.

---

## Pattern 4: Direct-to-S3 via Presigned URL

**Use Case:** Offload upload bandwidth from the application server; files go
straight to S3 from the client browser.

**Flow:**

1. Client requests presigned PUT URL from server → 2. Server generates URL →
2. Client uploads directly to S3 → 4. Client notifies server of completion →
3. Server verifies & creates DB record

### Step 1 — Get Presigned URL (Django)

```python
import uuid, boto3
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response


class GetPresignedUploadURLView(APIView):
    def post(self, request):
        filename = request.data["filename"]
        content_type = request.data.get("content_type", "application/octet-stream")
        tenant_schema = request.tenant.schema_name

        s3_key = f"tenant-{tenant_schema}/uploads/{uuid.uuid4()}/{filename}"

        client = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)
        presigned = client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": s3_key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

        return Response({"presigned_url": presigned, "s3_key": s3_key})
```

### Step 2 — Upload from Browser (JavaScript)

```javascript
async function uploadToS3(file) {
  // 1. Get presigned URL
  const res = await fetch("/api/presigned-upload-url/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({
      filename: file.name,
      content_type: file.type,
    }),
  });
  const { presigned_url, s3_key } = await res.json();

  // 2. PUT directly to S3
  const uploadRes = await fetch(presigned_url, {
    method: "PUT",
    headers: { "Content-Type": file.type },
    body: file,
  });
  if (!uploadRes.ok) throw new Error("S3 upload failed");

  // 3. Notify server
  await fetch("/api/upload-complete/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({ s3_key, filename: file.name }),
  });

  console.log("Direct-to-S3 upload complete!");
}
```

### Step 3 — Confirm Upload (Django)

```python
class UploadCompleteView(APIView):
    def post(self, request):
        s3_key = request.data["s3_key"]
        filename = request.data["filename"]

        client = boto3.client("s3")
        try:
            head = client.head_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key,
            )
        except client.exceptions.NoSuchKey:
            return Response({"error": "File not found"}, status=400)

        record = UploadedFile.objects.create(
            filename=filename,
            path=s3_key,
            size=head["ContentLength"],
        )

        return Response({"id": record.id, "size": head["ContentLength"]})
```

**Pros:** Eliminates server bandwidth bottleneck, highly scalable,
supports very large files without app server memory pressure.
**Cons:** Requires S3, CORS setup on the bucket, two-step flow.

---

## Pattern 5: Image Upload with Client-Side Preview & Compression

**Use Case:** Product image upload where the user sees a preview before
submitting, and the image is compressed client-side to speed up transfer.

### HTML

```html
<input type="file" id="image-input" accept="image/*" />
<img id="preview" style="max-width:300px; display:none;" />
<div id="file-info"></div>
<button id="upload-btn" onclick="uploadImage()" disabled>Upload</button>
<div id="status"></div>
```

### JavaScript (Preview + Client Compression)

```javascript
const imageInput = document.getElementById("image-input");

imageInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  // Instant preview via FileReader
  const reader = new FileReader();
  reader.onload = (evt) => {
    const preview = document.getElementById("preview");
    preview.src = evt.target.result;
    preview.style.display = "block";
  };
  reader.readAsDataURL(file);

  // Show file info
  document.getElementById("file-info").textContent = `${file.name} — ${(file.size / 1024 / 1024).toFixed(2)} MB`;
  document.getElementById("upload-btn").disabled = false;
});

async function uploadImage() {
  const file = imageInput.files[0];
  if (!file) return;

  document.getElementById("status").textContent = "Compressing…";

  // Client-side compression (requires browser-image-compression library)
  // <script src="https://cdn.jsdelivr.net/npm/browser-image-compression/dist/browser-image-compression.js"></script>
  let processedFile = file;
  if (typeof imageCompression !== "undefined") {
    processedFile = await imageCompression(file, {
      maxSizeMB: 1,
      maxWidthOrHeight: 1920,
      useWebWorker: true,
    });
  }

  document.getElementById("status").textContent = "Uploading…";

  const formData = new FormData();
  formData.append("image", processedFile, file.name);

  try {
    const resp = await fetch("/api/upload-image/", {
      method: "POST",
      headers: { "X-CSRFToken": getCsrfToken() },
      body: formData,
    });

    if (!resp.ok) throw new Error("Upload failed");

    const data = await resp.json();
    document.getElementById("status").textContent = "Done!";
    document.getElementById("preview").src = data.url;
  } catch (err) {
    document.getElementById("status").textContent = err.message;
  }
}
```

### Server Side (Same as Pattern 2)

The DRF `ImageUploadAPIView` from Pattern 2 handles the incoming file. The
server-side `ImageProcessor` applies additional optimisation (resize,
compress, format conversion, thumbnail generation) regardless of any
client-side compression.

**Pros:** Instant visual feedback, smaller upload payload, better UX.
**Cons:** Requires JS, preview may differ from final server-processed result,
needs the `browser-image-compression` library.

---

## Best Practices

1. **Always validate on the server** — never trust client-side checks alone.
2. **Choose the right pattern** — direct form for simple cases, AJAX for
   modern apps, chunked for large files, presigned URL for scale.
3. **Show progress** — upload progress and clear status messages.
4. **Handle errors gracefully** — display human-readable messages.
5. **Clean up temp files** — remove chunks after assembly.
6. **Set reasonable timeouts** — especially for large file uploads.
7. **Implement retry logic** — handle transient network failures.
8. **Validate extension + MIME** — defence in depth against spoofing.
9. **Set size limits** — prevent DoS and control storage costs.
10. **Use async processing** — Celery tasks for images ≥ 1 MB.

---

## Pattern Selection Guide

| Scenario                    | Recommended Pattern                    |
| --------------------------- | -------------------------------------- |
| Simple admin form           | Pattern 1 (Direct)                     |
| Product image upload        | Pattern 2 (AJAX) + Pattern 5 (Preview) |
| Invoice PDF upload          | Pattern 2 (AJAX)                       |
| Large backup/export         | Pattern 3 (Chunked)                    |
| High-traffic public uploads | Pattern 4 (Presigned S3)               |
| Mobile image capture        | Pattern 5 (Preview + Compress)         |
