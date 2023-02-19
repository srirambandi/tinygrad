from tinygrad.runtime.metal import CLBuffer, CLProgram

def benchmark(prog):
  e = prog()
  e.waitUntilCompleted()
  return (e.GPUEndTime() - e.GPUStartTime())*1e9
def mb(prog, N=10): return min([benchmark(prog) for _ in range(N)])

N = 2048
a = CLBuffer(N*N*4)
b = CLBuffer(N*N*4)
c = CLBuffer(N*N*4)

# 32 core GPU
# Each GPU core is split into 16 Execution Units, which each contain eight Arithmetic Logic Units (ALUs)
# clock = 1278MHz

# 32*16*8 = 4096 ALUs

prog = CLProgram("test", f"""
#include <metal_simdgroup_async>
using namespace metal;
kernel void test(device float4 *a, device float *data1, device float *data2, uint3 gid [[thread_position_in_grid]]) {{
  float4 acc0 = 0;
  threadgroup float ldata1[32*32];
  /*ldata1[gid.x] = 6;
  acc0 += data1[gid.x];
  int j = 0;
  a[gid.x] = ldata1[0] + 77;*/
  for (int i = 0; i < 128; i++) {{
    int s = i;
    simdgroup_async_copy(ldata1+i, data1, 16);
    simdgroup_async_copy(ldata1+i, data1, 32);
    //simdgroup_async_copy(ldata1+i, data1, 32*i);
    simdgroup_async_copy(ldata1, 8, 1, data1, 32, 1, ulong2(8, 32));
    simdgroup_async_copy(ldata1, 8, 1, data1, 64, 1, ulong2(8, 32));
    simdgroup_async_copy(ldata1, 8, 1, data1, 96, 1, ulong2(8, 32));
    /*auto future1 = simdgroup_async_copy(ldata1, data2, 8);
    auto future2 = simdgroup_async_copy(ldata1, data2, 8);
    auto future3 = simdgroup_async_copy(ldata1, data2, 8);
    auto future4 = simdgroup_async_copy(ldata1, data2, 8);
    future3.wait();*/

    //simdgroup_async_copy((threadgroup float4 *)ldata1, (device float4 *)data2, 8);

    /*simdgroup_async_copy(ldata1 + 0, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 + 1, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 + 2, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 +s+ 3, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 +s+ 4, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 +s+ 5, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 +s+ 6, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 +s+ 7, data2 + gid.z, 8);

    simdgroup_async_copy(data2 + gid.z, ldata1 +s+ 7, 8);*/

    /*simdgroup_async_copy(ldata1 + gid.x, data2 + gid.y, 8);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.z, 8);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.y + i, 8);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.z + i, 8);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.y, 16);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.z, 16);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.y + i, 16);
    simdgroup_async_copy(ldata1 + gid.x, data2 + gid.z + i, 16);
    simdgroup_async_copy(ldata1 + gid.y, data2 + gid.y, 58);
    simdgroup_async_copy(ldata1 + gid.y, data2 + gid.z, 58);
    simdgroup_async_copy(ldata1 + gid.y, data2 + gid.y + i, 58);
    simdgroup_async_copy(ldata1 + gid.y, data2 + gid.z + i, 58);*/
    //auto future1 = simdgroup_async_copy(ldata1 + i * 52, data2 + i*47, 67);
    //auto future1 = simdgroup_async_copy(ldata1 + i * 52, data2 + i*47, 67);
    //auto future2 = simdgroup_async_copy(data1 + i * 33, ldata1 + i * 99, 84);
    //future1.wait();
    //future2.wait();
    //j += 7;
  }}
  //__metal_simdgroup_event_t event;
  //__metal_threadgroup_event_t event;
  //__metal_async_wg_copy((threadgroup char*)&ldata1[0], (device char*)data1, 32, event);
  //__metal_wait_wg_events(1, &event);
  /*for (uint i = 0; i < 4096; i+=4) {{
    float4 r0 = float4(data1[i]);
    float4 r1 = float4(data1[i+1]);
    float4 r2 = float4(data1[i+2]);
    acc0.x += dot(r0, r0);
    acc0.y += dot(r0, r1);
    acc0.z += dot(r0, r2);
    acc0.w += dot(r1, r2);
  }}*/
  a[gid.x] = acc0;
}}""")
#      fma  float4   statements    loop
FLOPS = 2 *   4    *    4      *   1024
sz = 512*512
#tm = mb(lambda: prog([sz,1,1], [32,1,1], a._cl, b._cl, c._cl))
#print(f"{sz:10d} {tm*1e-3:9.2f} us {tm/sz:7.3f} ns/kernel -- {sz*FLOPS/tm:10.3f} GFLOPS")
