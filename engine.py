"""Bounded, deterministic consensus agent. No invented Qloo scores."""
import json, os, time, urllib.parse, urllib.request, urllib.error

class ProviderError(Exception): pass
class Qloo:
    mode = 'live'
    def __init__(self, key=None, opener=None):
        self.key = key or os.environ.get('QLOO_API_KEY')
        self.opener = opener or urllib.request.urlopen
    def get(self, path, params):
        if not self.key: raise ProviderError('Qloo API key is not configured. Live access is unavailable.')
        req = urllib.request.Request('https://hackathon.api.qloo.com'+path+'?'+urllib.parse.urlencode(params), headers={'X-Api-Key':self.key,'Accept':'application/json'})
        try:
            with self.opener(req, timeout=12) as response:
                raw = response.read(2_000_001)
            if len(raw)>2_000_000: raise ProviderError('Qloo response exceeded the safety limit.')
            data=json.loads(raw)
            if not isinstance(data,dict) or data.get('success') is False: raise ProviderError('Qloo rejected the request.')
            return data
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise ProviderError('Qloo request failed. Check key access, quota, and connectivity; no sample results were substituted.') from exc
    def search(self, query):
        data=self.get('/search',{'query':query,'types':'urn:entity:movie','take':5})
        return normalize(data.get('results'))
    def recommend(self, seed):
        data=self.get('/v2/insights',{'filter.type':'urn:entity:movie','signal.interests.entities':seed,'take':20})
        results=data.get('results',{})
        if not isinstance(results,dict): raise ProviderError('Unexpected Qloo insights schema.')
        return normalize(results.get('entities'))

def normalize(rows):
    if not isinstance(rows,list): raise ProviderError('Unexpected Qloo entity schema.')
    result=[]; seen=set()
    for row in rows:
        if not isinstance(row,dict): raise ProviderError('Malformed Qloo entity.')
        eid=row.get('entity_id'); name=row.get('name')
        if not isinstance(eid,str) or not isinstance(name,str) or not eid or not name: raise ProviderError('Qloo entity missing identity or name.')
        if eid not in seen:
            result.append({'id':eid,'name':name[:200]}); seen.add(eid)
    return result

# Authored fictional fixtures, not Qloo data or real film recommendations.
MOVIES=[{'id':f'fixture-{i}','name':name} for i,name in enumerate(['Orbit Letters','The Quiet Garden','Midnight Algorithm','Paper Cities','The Long Way Home','Starlight Kitchen','Small Wonders'])]
class Fixture:
    mode='fixture'
    def search(self,query):
        return [m for m in MOVIES if query.casefold() in m['name'].casefold()][:5]
    def recommend(self,seed):
        orders={'fixture-0':[2,3,4,5,6], 'fixture-1':[6,5,4,2,3], 'fixture-2':[3,4,0,6,5]}
        if seed not in {m['id'] for m in MOVIES}: raise ProviderError('Unknown fixture seed.')
        return [MOVIES[i] for i in orders.get(seed,[0,1,2,4,6]) if MOVIES[i]['id']!=seed]

def consensus(lists,seeds,policy='fair'):
    """Rank-position utility is our heuristic, never an API probability."""
    if policy not in ('fair','average'): raise ValueError('Unknown policy')
    all_ids={x['id'] for rows in lists for x in rows}-set(seeds)
    names={x['id']:x['name'] for rows in lists for x in rows}
    rows=[]
    for eid in all_ids:
        positions=[next((i+1 for i,x in enumerate(xs) if x['id']==eid),None) for xs in lists]
        utilities=[(len(xs)-p+1)/len(xs) if p is not None else 0 for xs,p in zip(lists,positions)]
        rows.append({'id':eid,'name':names[eid],'positions':positions,'utilities':utilities,'floor':min(utilities),'average':sum(utilities)/len(lists),'coverage':sum(p is not None for p in positions)})
    key=(lambda x:(-x['floor'],-x['average'],x['id'])) if policy=='fair' else (lambda x:(-x['average'],-x['floor'],x['id']))
    return sorted(rows,key=key)

def plan(provider,members,policy):
    if not isinstance(members,list) or not 2<=len(members)<=4: raise ValueError('Choose two to four people.')
    if policy not in ('fair','average'): raise ValueError('Choose a valid ranking policy.')
    clean=[]
    for i,m in enumerate(members):
        if not isinstance(m,dict): raise ValueError('Invalid person.')
        eid=m.get('id'); name=m.get('name'); label=m.get('label',f'Person {i+1}')
        if not all(isinstance(s,str) and 0<len(s)<=200 for s in (eid,name,label)): raise ValueError('Select a movie for every person.')
        clean.append({'id':eid,'label':label,'name':name})
    trace=[{'step':'Plan','detail':f'Fetch one bounded candidate list for each of {len(clean)} participants.'}]
    lists=[]
    # Re-resolve IDs against search to avoid accepting arbitrary client labels as Qloo evidence.
    for member in clean:
        found=provider.search(member['name'])
        match=next((x for x in found if x['id']==member['id']),None)
        if not match: raise ValueError('A selected movie could not be verified. Search and select it again.')
        member['name']=match['name']; candidates=provider.recommend(member['id']); lists.append(candidates)
        trace.append({'step':'Retrieve','detail':f"{member['label']}: {len(candidates)} candidates for {match['name']}."})
    rows=consensus(lists,[m['id'] for m in clean],policy)
    baseline=consensus(lists,[m['id'] for m in clean],'average')
    trace.append({'step':'Negotiate','detail':'Compare the minimum per-person rank utility, then average utility.' if policy=='fair' else 'Compare average rank utility, then minimum utility.'})
    trace.append({'step':'Verify','detail':'Exclude seed movies. Missing candidates mean unknown coverage, not proven dislike. No availability or content-safety claims.'})
    warnings=[]
    if not rows: warnings.append('No candidates returned. Try different seeds; the agent cannot infer a compromise.')
    elif rows[0]['coverage']<len(clean): warnings.append('No candidate appears in every retrieved list. This shortlist has incomplete evidence for at least one person.')
    return {'mode':provider.mode,'members':clean,'policy':policy,'results':rows[:8],'baseline':baseline[:1],'trace':trace,'warnings':warnings,'generated_at':int(time.time()),'method':'Utility = (list length − rank + 1) / list length; absent = 0 for conservative ranking. This is a local heuristic, not a Qloo score or satisfaction probability.'}
