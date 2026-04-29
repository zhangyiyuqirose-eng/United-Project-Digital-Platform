<template>
  <div class="dialog-overlay" v-if="visible" @click.self="emit('close')">
    <div class="dialog-card">
      <div class="dialog-header">
        <h3>{{ editingId ? '编辑合同' : '新增合同' }}</h3>
        <button class="close-btn" @click="emit('close')">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
      </div>

      <div class="dialog-body">
        <div class="form-section">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">合同名称</label>
              <input v-model="form.contractName" type="text" class="form-input" placeholder="请输入合同名称">
            </div>
            <div class="form-group">
              <label class="form-label">合同类型</label>
              <select v-model="form.contractType" class="form-select">
                <option value="">请选择</option>
                <option value="SALES">销售合同</option>
                <option value="PROCUREMENT">采购合同</option>
                <option value="FRAMEWORK">框架协议</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">关联项目</label>
              <input v-model="form.projectId" type="text" class="form-input" placeholder="请输入项目ID">
            </div>
            <div class="form-group">
              <label class="form-label">相对方</label>
              <input v-model="form.counterparty" type="text" class="form-input" placeholder="请输入合同相对方">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">合同金额</label>
              <input v-model.number="form.amount" type="number" class="form-input" placeholder="请输入金额">
            </div>
            <div class="form-group">
              <label class="form-label">签署日期</label>
              <input v-model="form.signDate" type="date" class="form-input">
            </div>
          </div>
          <div class="form-row full">
            <div class="form-group full">
              <label class="form-label">备注说明</label>
              <textarea v-model="form.description" class="form-textarea" rows="3" placeholder="请输入备注..."></textarea>
            </div>
          </div>
        </div>
      </div>

      <div class="dialog-footer">
        <button class="cancel-btn" @click="emit('close')">取消</button>
        <button class="submit-btn" @click="handleSubmit">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createContract, updateContract } from '@/api/modules/business'

const props = defineProps<{
  visible: boolean
  editingId: string
  editingData: Record<string, any>
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const defaultForm = () => ({ contractName: '', contractType: '', projectId: '', counterparty: '', amount: 0, signDate: '', description: '' })

const form = reactive(defaultForm())

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editingId && props.editingData) {
      Object.assign(form, {
        contractName: props.editingData.contractName || '',
        contractType: props.editingData.contractType || '',
        projectId: props.editingData.projectId || '',
        counterparty: props.editingData.counterparty || '',
        amount: props.editingData.amount || 0,
        signDate: props.editingData.signDate || '',
        description: props.editingData.description || '',
      })
    } else {
      Object.assign(form, defaultForm())
    }
  }
})

async function handleSubmit() {
  if (!form.contractName || !form.contractType) {
    ElMessage.warning('请填写合同名称和类型')
    return
  }
  try {
    if (props.editingId) {
      await updateContract(props.editingId, form)
    } else {
      await createContract(form)
    }
    ElMessage.success('保存成功')
    emit('saved')
    emit('close')
  } catch { /* handled */ }
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
    width: 600px;
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

      .form-section {
        .form-row {
          display: flex;
          gap: $spacing-lg;
          margin-bottom: $spacing-lg;
          &.full { display: block; }

          .form-group {
            flex: 1;
            &.full { width: 100%; }

            .form-label {
              font-size: $font-size-sm;
              font-weight: $font-weight-medium;
              color: $text-secondary;
              margin-bottom: $spacing-sm;
              display: block;
            }

            .form-input, .form-select {
              width: 100%;
              padding: 12px 16px;
              background: $bg-secondary;
              border: 2px solid transparent;
              border-radius: $radius-lg;
              font-size: $font-size-md;
              color: $text-primary;
              transition: all 0.25s ease;
              &:hover { background: $bg-tertiary; }
              &:focus {
                background: white;
                border-color: $accent-color;
                box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.1);
              }
            }

            .form-textarea {
              width: 100%;
              padding: $spacing-md;
              background: $bg-secondary;
              border: 2px solid transparent;
              border-radius: $radius-lg;
              font-size: $font-size-md;
              color: $text-primary;
              resize: none;
              transition: all 0.25s ease;
              &:hover { background: $bg-tertiary; }
              &:focus {
                background: white;
                border-color: $accent-color;
                box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.1);
              }
            }
          }
        }
      }
    }

    .dialog-footer {
      display: flex;
      gap: $spacing-sm;
      padding: $spacing-lg;
      border-top: 1px solid $divider-color;

      .cancel-btn, .submit-btn {
        flex: 1;
        padding: 12px;
        border-radius: $radius-lg;
        font-size: $font-size-md;
        font-weight: $font-weight-medium;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .cancel-btn {
        background: $bg-secondary;
        border: 1px solid $border-color;
        color: $text-secondary;
        &:hover { background: $bg-tertiary; }
      }

      .submit-btn {
        background: $accent-gradient;
        border: none;
        color: white;
        &:hover { transform: translateY(-1px); box-shadow: $shadow-md; }
      }
    }
  }
}

@keyframes dialogEnter {
  from { opacity: 0; transform: translateY(-20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
