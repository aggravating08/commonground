import { configured,reply } from '../../../lib/demo-api';
export function GET(){return reply({live_configured:configured(),live_verified:false})}
