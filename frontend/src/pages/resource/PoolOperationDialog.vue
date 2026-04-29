<template>
  <div class="dialog-overlay" v-if="visible" @click.self="emit('close')">
    <div class="dialog-card">
      <div class="dialog-header">
        <h3>分配资源到项目</h3>
        <button class="close-btn" @click="emit('close')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
      </div>
      <div class="dialog-body">
        <div class="selected-resource">
          <span class="resource-label">选中人员:</span>
          <span class="resource-value">{{ resource?.name }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">目标项目</label>
          <div class="form-input">
            <input type="text" v-model="projectId" placeholder="请输入项目ID">
          </div>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="cancel-btn" @click="emit('close')">取消</button>
        <button class="confirm-btn" @click="handleConfirm">确认分配</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { PersonVO } from '@/api/modules/resource'

const props = defineProps<{
  visible: boolean
  resource: PersonVO | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'confirmed'): void
}>()

const projectId = ref('')

watch(() => props.visible, (val) => { if (val) projectId.value = '' })

function handleConfirm() {
  if (!projectId.value) {
    ElMessage.warning('请输入项目ID')
    return
  }
  ElMessage.success('分配成功')
  emit('confirmed')
  emit('close')
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .dialog-card {
    background: white;
    border-radius: $radius-xl;
    width: 400px;
    max-width: 90vw;
    animation: dialogEnter 0.3s ease;

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-lg;
      border-bottom: 1px solid $divider-color;

      h3 { font-size: $font-size-lg; font-weight: $font-weight-semibold; color: $text-primary; }

      .close-btn {
        width: 32px;
        height: 32px;
        border-radius: $radius-md;
        background: transparent;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: $text-muted;
        svg { width: 20px; height: 20px; }
        &:hover { background: $bg-secondary; color: $danger-color; }
      }
    }

    .dialog-body {
      padding: $spacing-lg;

      .selected-resource {
        display: flex;
        gap: $spacing-sm;
        margin-bottom: $spacing-lg;
        .resource-label { font-size: $font-size-sm; color: $text-muted; }
        .resource-value { font-size: $font-size-md; font-weight: $font-weight-medium; color: $text-primary; }
      }

      .form-group {
        .form-label {
          font-size: $font-size-sm;
          font-weight: $font-weight-medium;
          color: $text-secondary;
          margin-bottom: $spacing-sm;
          display: block;
        }

        .form-input input {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid $border-color;
          border-radius: $radius-lg;
          font-size: $font-size-md;
          color: $text-primary;
          transition: all 0.2s ease;
          &:focus { border-color: $accent-color; box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.1); }
        }
      }
    }

    .dialog-footer {
      display: flex;
      gap: $spacing-sm;
      padding: $spacing-lg;
      border-top: 1px solid $divider-color;

      .cancel-btn, .confirm-btn {
        flex: 1;
        padding: 12px;
        border-radius: $radius-lg;
        font-size: $font-size-md;
        font-weight: $font-weight-medium;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .cancel-btn { background: $bg-secondary; border: 1px solid $border-color; color: $text-secondary; &:hover { background: $bg-tertiary; } }
      .confirm-btn { background: $accent-gradient; border: none; color: white; &:hover { transform: translateY(-1px); box-shadow: $shadow-md; } }
    }
  }
}

@keyframes dialogEnter {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
