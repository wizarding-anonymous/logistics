import React, { useState } from 'react';
import { useSubmitReview } from '@/hooks/useOrder';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '../ui/label';

export function LeaveReviewForm({ orderId }: { orderId: string }) {
  const { mutate: submitReview, isPending, isSuccess } = useSubmitReview();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitReview({ orderId, payload: { rating, comment } });
  };

  if (isSuccess) {
    return <p className="text-green-600">Thank you for your review!</p>;
  }

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Leave a Review</CardTitle>
        <CardDescription>How was your experience with this order?</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Rating (1-5)</Label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <Button
                  key={star}
                  type="button"
                  variant={rating >= star ? 'default' : 'outline'}
                  onClick={() => setRating(star)}
                >
                  {star}
                </Button>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="comment">Comment</Label>
            <Textarea
              id="comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us more..."
            />
          </div>
          <Button type="submit" disabled={isPending}>
            {isPending ? 'Submitting...' : 'Submit Review'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
