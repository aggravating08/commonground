import { env } from 'cloudflare:workers';
import { Qloo, Fixture, ProviderError } from './consensus.mjs';
let active=0;let timestamps:number[]=[];
export function configured(){return Boolean((env as Record<string,unknown>).QLOO_API_KEY)}
export function provider(mode:string){if(mode==='fixture')return new Fixture();if(mode==='live')return new Qloo((env as Record<string,unknown>).QLOO_API_KEY);throw Error('Invalid data mode')}
export function reply(data:unknown,status=200){return Response.json(data,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}})}
export async function bounded(fn:()=>Promise<unknown>){const now=Date.now();timestamps=timestamps.filter(x=>now-x<60000);if(timestamps.length>=20||active>=2)return reply({error:'Demo request limit reached. Try again shortly.'},429);timestamps.push(now);active++;try{return reply(await fn())}catch(e){return reply({error:e instanceof Error?e.message:'Request failed'},e instanceof ProviderError?502:400)}finally{active--}}
