import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

const REVALIDATION_SECRET = process.env.REVALIDATION_SECRET || '';

export async function POST(request: NextRequest) {
  // Validate secret token
  const authHeader = request.headers.get('authorization');
  const token = authHeader?.replace('Bearer ', '');

  if (!REVALIDATION_SECRET || token !== REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { type, path, tag } = body as {
      type?: 'path' | 'tag';
      path?: string;
      tag?: string;
    };

    if (type === 'path' && path) {
      revalidatePath(path);
      return NextResponse.json({ revalidated: true, path, timestamp: Date.now() });
    }

    if (type === 'tag' && tag) {
      revalidateTag(tag);
      return NextResponse.json({ revalidated: true, tag, timestamp: Date.now() });
    }

    return NextResponse.json(
      { error: 'Missing required fields: type (path|tag) and path/tag value' },
      { status: 400 }
    );
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 });
  }
}
