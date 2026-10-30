# CommonGround hosted runtime

Vinext/Cloudflare port of the Python demo in the parent directory. It serves the same interface from public/app.html and implements server-side Qloo Search and Insights routes. Keys are read from the QLOO_API_KEY runtime secret, never client code. No connector permissions or persistent storage are used.

`node --test tests/consensus.test.mjs` runs six network-free tests. `npm run dev` runs local preview; use the Sites build/source workflow for hosting. API verification remains pending key approval. Fixture films and rankings are original synthetic examples.

The request guard allows 20 operations/minute and two simultaneous operations per Worker isolate. It is not a global or account spending cap. Set provider quotas before configuring live public access.
