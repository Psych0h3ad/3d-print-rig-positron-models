"""Rebuild the assembled display from native BREP leaves, with print supports omitted."""
from pathlib import Path
import argparse,gzip,hashlib,io,json
import cadquery as cq,numpy as np,trimesh
from OCP.BRepTools import BRepTools
from native_mesh import clean_mesh,small_hardware

# Explicitly inspected support solids. The two-part lip spool holder is retained.
KEEP={'00118':[0],'00136':[0],'00459':[0],'00556':[0],'00560':[1]}
def rebuild(cache,model,report):
 manifest=json.loads((model/'assembly_manifest.json').read_text())
 profile=json.loads((model/'machine_profile.json').read_text())
 rows={r['id']:r for r in json.loads((cache/'inventory.json').read_text(encoding='utf8'))}
 old=trimesh.load_scene(io.BytesIO(gzip.decompress((model/'model.glb.gz').read_bytes())),file_type='glb',process=False)
 meshes={m.metadata['part_key']:m for m in old.geometry.values()}
 result=trimesh.Scene();origin=np.array(profile['native_origin_mm']);audit=[]
 hardware={'00094','00095','00097','00098','00132','00133','00462','00463','00467','00468'}
 for i,p in enumerate(manifest['parts']):
  key=p['key'];shape=cq.Shape.importBrep(str(cache/(key+'.brep')));source=shape;solids=shape.Solids()
  removed=[]
  if key in KEEP:
   removed=[dict(index=j,volume_mm3=s.Volume())for j,s in enumerate(solids)if j not in KEEP[key]]
   shape=cq.Compound.makeCompound([solids[j]for j in KEEP[key]])
   p['print_supports_omitted']=removed
  BRepTools.Clean_s(shape.wrapped)
  small=small_hardware(rows[key]['name'],'native')
  v,f=shape.tessellate(.3,.6)if small else shape.tessellate(.2,.3)
  xyz=np.array([q.toTuple()for q in v])-origin
  xyz=xyz[:,[0,2,1]]*[.001,.001,-.001]
  native=trimesh.Trimesh(vertices=xyz,faces=f,process=False)
  native.merge_vertices(digits_vertex=8)
  corrected=False
  if not native.is_winding_consistent:
   trimesh.repair.fix_winding(native);corrected=True
  try:mesh=clean_mesh(native,reduce=small)
  except AssertionError:raise ValueError('Inconsistent native surface '+key)from None
  previous=meshes[key];mesh.visual=previous.visual.copy();mesh.metadata=previous.metadata.copy()
  if key in hardware:
   p['appearance_role']='native';mesh.metadata['appearance_role']='native'
   mesh.visual.material.baseColorFactor=np.array([170,174,180,255],dtype=np.uint8)
   mesh.visual.material.metallicFactor=.6
  if not rows[key]['valid']:p['source_reference_only']=True
  result.add_geometry(mesh,geom_name='part_'+key,node_name='part_'+key)
  audit.append(dict(key=key,source_valid=rows[key]['valid'],source_faces=len(source.Faces()),triangles=len(mesh.faces),removed_supports=removed,decimated=len(mesh.faces)<len(native.faces),winding_corrected=corrected,winding_consistent=mesh.is_winding_consistent,normals_unit=bool(np.allclose(np.linalg.norm(mesh.vertex_normals,axis=1),1,atol=1e-5))))
  if i%100==0:print('native surfaces',i,flush=True)
 raw=result.export(file_type='glb',include_normals=True)
 packed=gzip.compress(raw,9,mtime=0);(model/'model.glb.gz').write_bytes(packed)
 manifest['triangles']=sum(a['triangles']for a in audit)
 manifest['display_mesh']='Native CAD surfaces welded and shaded. Small fasteners reduced only after topology, winding and bounds checks. Motor, housing, rail, hinge and probe surfaces are retained. Identified built-in print supports omitted; original invalid reference leaves retained as reference geometry.'
 manifest['print_supports_omitted']=[a for a in audit if a['removed_supports']]
 (model/'assembly_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
 index=json.loads((model/'ASSET_INDEX.json').read_text())
 for name,spec in index['files'].items():
  b=(model/spec['path']).read_bytes();spec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if name=='model.glb':spec.update(decoded_bytes=len(raw),decoded_sha256=hashlib.sha256(raw).hexdigest())
 index['version']='positron-native-surfaces-70'
 (model/'ASSET_INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
 evidence=dict(all_passed=all(a['winding_consistent']and a['normals_unit']for a in audit),parts=len(audit),model_sha256=hashlib.sha256(raw).hexdigest(),compressed_bytes=len(packed),triangles=manifest['triangles'],supports_omitted=sum(len(a['removed_supports'])for a in audit),results=audit)
 report.write_text(json.dumps(evidence,indent=2)+'\n');print('DONE',len(audit),len(packed),evidence['supports_omitted'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();rebuild(a.cache,a.model,a.report)
