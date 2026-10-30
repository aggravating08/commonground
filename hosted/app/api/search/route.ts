import { bounded,provider } from '../../../lib/demo-api';
export async function GET(request:Request){return bounded(async()=>{const p=new URL(request.url).searchParams,q=(p.get('q')||'').trim(),mode=p.get('mode')||'fixture';if(q.length<2||q.length>100)throw Error('Search needs 2–100 characters.');return {mode,results:await provider(mode).search(q)}})}
