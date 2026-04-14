# Sign-In Email Pre-Fill — Required App Change

## Context

The HubSign landing page (`hubsign.io`) redirects users who choose **Shared Instance** to `app.hubsign.io/signin` with their email passed as a query parameter:

```
https://app.hubsign.io/signin?email=user@example.com
```

For the email field to be pre-filled on arrival, the **app's signin page** needs to read that query param and set it as the default value of the email input.

---

## Change Required

### Next.js App Router (`app/signin/page.tsx`)

```tsx
'use client';

import { useSearchParams } from 'next/navigation';

export default function SignInPage() {
  const searchParams = useSearchParams();
  const emailFromUrl = searchParams.get('email') ?? '';

  return (
    // ... your existing layout ...
    <input
      type="email"
      name="email"
      defaultValue={emailFromUrl}
      autoFocus={!!emailFromUrl}
      // ... your existing props ...
    />
  );
}
```

### Next.js Pages Router (`pages/signin.tsx`)

```tsx
import { GetServerSideProps } from 'next';

export const getServerSideProps: GetServerSideProps = async ({ query }) => {
  return {
    props: {
      prefillEmail: (query.email as string) ?? '',
    },
  };
};

export default function SignInPage({ prefillEmail }: { prefillEmail: string }) {
  return (
    // ... your existing layout ...
    <input
      type="email"
      name="email"
      defaultValue={prefillEmail}
      autoFocus={!!prefillEmail}
      // ... your existing props ...
    />
  );
}
```

---

## Summary

| What | Where | Change |
|------|-------|--------|
| Read `?email=` param | `app/signin/page.tsx` or `pages/signin.tsx` | Add `useSearchParams` or `getServerSideProps` |
| Pre-fill email input | Email `<input>` element | Set `defaultValue={emailFromUrl}` |
| Auto-focus (optional) | Same input | Set `autoFocus={!!emailFromUrl}` |

No backend changes are required. This is a frontend-only read of a URL query parameter.
