.global _start
_start:
.rodata
.align 0x10
.global code.kd
.type code.kd,STT_OBJECT
code.kd:
.long 0,0,0,0
# NOTE: the real one has 0x00000b40 here, but that doesn't work
.long 0x00000bc0,0x00000000,0x00000000,0x00000000
.long 0,0,0,0
.long 0x60af0000,0x0000009e,0x00000408,0x00000000

.text
.global code
.type code,STT_FUNC
code:
s_load_b64 s[0:1], s[0:1], null

# v_dual_mov_b32 v0, 4 :: v_dual_mov_b32 v1, 2.0
v_mov_b32 v0, 4
v_mov_b32 v1, 2.0
s_waitcnt lgkmcnt(0)

global_store_b32 v0, v1, s[0:1]

# Deallocate all VGPRs for this wave. Use only when next instruction is S_ENDPGM.
s_sendmsg sendmsg(MSG_DEALLOC_VGPRS)
s_endpgm
s_code_end

.amdgpu_metadata
amdhsa.kernels:
  - .args:
      - .address_space:  global
        .name:           a
        .offset:         0
        .size:           8
        .type_name:      'float*'
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 8
    .language:       OpenCL C
    .language_version:
      - 1
      - 2
    .max_flat_workgroup_size: 256
    .name:           code
    .private_segment_fixed_size: 0
    .sgpr_count:     2
    .sgpr_spill_count: 0
    .symbol:         code.kd
    .uses_dynamic_stack: false
    .vgpr_count:     2
    .vgpr_spill_count: 0
    .wavefront_size: 32
amdhsa.target:   amdgcn-amd-amdhsa--gfx1100
amdhsa.version:
  - 1
  - 2
.end_amdgpu_metadata
