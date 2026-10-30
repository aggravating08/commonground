import type { Metadata } from 'next';
export const metadata: Metadata = {title:'CommonGround — Find your shared screen',description:'Transparent group movie-night negotiation.'};
export default function Layout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}</body></html>}
