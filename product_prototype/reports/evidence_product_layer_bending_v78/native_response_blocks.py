"""Expand actual Native constraint GROUP metadata into all 3-row friction contacts.
first_row belongs to an entire response group,NOT necessarily one contact.
Reject unsupported/incomplete layouts;never infer normal rows from global row ID.
"""
def friction_blocks(responses,time_s,direct_ids):
 groups={}
 for r in responses:
  if float(r['time_s'])!=time_s:continue
  key=(r['constraint_path'],int(r['first_row']));groups.setdefault(key,set()).add(int(r['row_id']))
 blocks=[];covered=set()
 for (_,first),ids in groups.items():
  if len(ids)%3 or ids!=set(range(first,first+len(ids))):raise ValueError('unsupported/incomplete actual response friction group')
  for b in range(first,first+len(ids),3):blocks.append(b)
  covered.update(ids)
 if covered!=set(direct_ids):raise ValueError('response does not cover all actual direct contact rows')
 if len(blocks)!=len(set(blocks)):raise ValueError('overlapping response group ownership')
 return sorted(blocks)
