'use client';

import { useState } from 'react';
import { useForm, type Resolver } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import { cn } from '@/lib/cn';
import { loginSchema, type LoginFormData } from '@/lib/validations/login';
import { authService } from '@/services/api/authService';
import { useAuthStore } from '@/stores/useAuthStore';
import { getIntendedUrl } from './ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { AuthAlert } from './AuthAlert';
import { AuthDivider } from './AuthDivider';
import { SocialLoginButtons } from './SocialLoginButtons';

export interface LoginFormProps {
  onSuccess?: () => void;
  redirectUrl?: string;
}

export function LoginForm({ onSuccess, redirectUrl = '/dashboard' }: LoginFormProps) {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const authStore = useAuthStore();

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema) as Resolver<LoginFormData>,
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
    mode: 'onBlur',
  });

  async function onSubmit(data: LoginFormData) {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login({
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe,
      });

      // Check if 2FA is required
      if ((response as unknown as { require2FA?: boolean; sessionToken?: string }).require2FA) {
        const sessionToken = (response as unknown as { sessionToken: string }).sessionToken;
        router.push(`/two-factor/verify?session=${encodeURIComponent(sessionToken)}`);
        return;
      }

      // Update auth store with login action (sets isAuthenticated = true)
      authStore.login(
        {
          id: response.user.id,
          email: response.user.email,
          firstName: response.user.firstName,
          lastName: response.user.lastName,
          role: response.user.role,
          avatar: response.user.avatar ?? null,
        },
        null as never, // tenant is set separately if applicable
        response.user.permissions ?? []
      );

      if (onSuccess) {
        onSuccess();
      } else {
        const intendedUrl = getIntendedUrl();
        router.push(intendedUrl || redirectUrl);
      }
    } catch (err: unknown) {
      const errorObj = err as { response?: { status?: number; data?: { message?: string } } };
      const status = errorObj?.response?.status;
      const message = errorObj?.response?.data?.message;

      if (status === 401) {
        setError('Invalid email or password. Please try again.');
      } else if (status === 423) {
        setError(
          'Your account has been locked due to too many failed attempts. Please contact support.'
        );
      } else if (status === 429) {
        setError('Too many login attempts. Please try again later.');
      } else if (message) {
        setError(message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {error && <AuthAlert type="error" message={error} onClose={() => setError(null)} />}

        {/* Email */}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="name@company.com"
                  autoComplete="email"
                  inputMode="email"
                  disabled={isLoading}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Password */}
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    className="pr-10"
                    disabled={isLoading}
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 transition-colors hover:text-gray-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Remember me & Forgot password */}
        <div className="flex items-center justify-between">
          <FormField
            control={form.control}
            name="rememberMe"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center space-x-2 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                    disabled={isLoading}
                  />
                </FormControl>
                <FormLabel className="cursor-pointer text-sm font-normal">Remember me</FormLabel>
              </FormItem>
            )}
          />
          <Link
            href="/forgot-password"
            className="text-sm font-medium text-blue-600 transition-colors hover:text-blue-800 hover:underline dark:text-blue-400 dark:hover:text-blue-300"
          >
            Forgot password?
          </Link>
        </div>

        {/* Submit */}
        <Button
          type="submit"
          className="w-full"
          size="lg"
          loading={isLoading}
          disabled={isLoading}
          aria-busy={isLoading}
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
        </Button>

        {/* Divider + Social */}
        <AuthDivider text="or continue with" />
        <SocialLoginButtons disabled={isLoading} />
      </form>
    </Form>
  );
}
