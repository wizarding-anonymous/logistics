import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '@/services/authService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
// import ReCAPTCHA from 'react-google-recaptcha';

// const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || "your_recaptcha_site_key_here";

function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('client');
  // const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  // const recaptchaRef = useRef<ReCAPTCHA>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    // TODO: Re-enable reCAPTCHA in production
    // if (!recaptchaToken) {
    //   setError("Please complete the reCAPTCHA.");
    //   setIsSubmitting(false);
    //   return;
    // }

    try {
      await registerUser({
        email,
        password,
        // recaptcha_token: recaptchaToken,
        recaptcha_token: "mock_token_for_dev", // Mocking token
        roles: [role]
      });
      navigate('/login?status=registered');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during registration.');
      // recaptchaRef.current?.reset();
      // setRecaptchaToken(null);
    } finally {
        setIsSubmitting(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Create an Account</CardTitle>
          <CardDescription>Enter your details to get started.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="name@example.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                placeholder="••••••••"
              />
            </div>
            <div className="space-y-2">
                <Label>I am a...</Label>
                <RadioGroup defaultValue="client" value={role} onValueChange={setRole} className="flex space-x-4">
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="client" id="r-client" />
                        <Label htmlFor="r-client">Client (Shipper)</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="supplier" id="r-supplier" />
                        <Label htmlFor="r-supplier">Supplier (Carrier)</Label>
                    </div>
                </RadioGroup>
            </div>

            {/* <ReCAPTCHA
              ref={recaptchaRef}
              sitekey={RECAPTCHA_SITE_KEY}
              onChange={(token) => setRecaptchaToken(token)}
              onExpired={() => setRecaptchaToken(null)}
            /> */}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? 'Registering...' : 'Create Account'}
            </Button>
            {error && <p className="text-sm text-red-600 text-center">{error}</p>}
          </form>
          <div className="mt-4 text-center text-sm">
            Already have an account?{' '}
            <Link to="/login" className="underline">
              Login here
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default RegisterPage;
