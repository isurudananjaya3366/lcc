/**
 * Newsletter Email Validation
 */

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const DISPOSABLE_DOMAINS = [
  'mailinator.com',
  'guerrillamail.com',
  'tempmail.com',
  'throwaway.email',
  'yopmail.com',
  'trashmail.com',
  'sharklasers.com',
  'guerrillamailblock.com',
  'grr.la',
  'guerrillamail.info',
  'guerrillamail.biz',
  'guerrillamail.de',
  'guerrillamail.net',
  'guerrillamail.org',
  'spam4.me',
  'maildrop.cc',
  'discard.email',
  'fakeinbox.com',
];

export interface EmailValidationResult {
  valid: boolean;
  message: string;
}

/**
 * Validates an email address with:
 * - Format regex check
 * - Maximum length check (254 per RFC 5321)
 * - Disposable domain check
 */
export function validateEmail(email: string): EmailValidationResult {
  const trimmed = email.trim();

  if (!trimmed) {
    return { valid: false, message: 'Email address is required.' };
  }

  if (trimmed.length > 254) {
    return { valid: false, message: 'Email address is too long.' };
  }

  if (!EMAIL_REGEX.test(trimmed)) {
    return { valid: false, message: 'Please enter a valid email address.' };
  }

  const domain = trimmed.split('@')[1]?.toLowerCase();
  if (domain && DISPOSABLE_DOMAINS.includes(domain)) {
    return { valid: false, message: 'Disposable email addresses are not allowed. Please use a permanent address.' };
  }

  return { valid: true, message: '' };
}
