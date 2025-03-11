<template>
  <div class="attacks-view">
    <div class="page-title">
      <h1>Jailbreak Attacks</h1>
      <Button label="Create New Attack" icon="pi pi-plus" @click="openNewAttackDialog" />
    </div>
    
    <Card>
      <template #content>
        <div class="filter-container">
          <div class="search-container">
            <InputText v-model="filters.global.value" placeholder="Search by name..." class="search-input" />
            <i class="pi pi-search search-icon"></i>
          </div>
          <div class="filter-dropdown">
            <Dropdown v-model="selectedAlgorithmType" :options="algorithmTypeOptions" optionLabel="name" 
                      placeholder="Filter by algorithm type" @change="filterByAlgorithmType" />
          </div>
        </div>
        
        <!-- 添加批量操作工具栏 -->
        <div class="bulk-actions" v-if="selectedAttacks.length > 0">
          <span class="selected-count">已选择 {{ selectedAttacks.length }} 项</span>
          <div class="bulk-actions-buttons">
            <Button label="批量删除" icon="pi pi-trash" severity="danger" @click="confirmDeleteSelectedAttacks" />
          </div>
        </div>
        
        <div v-if="loading" class="loading-container">
          <ProgressSpinner />
        </div>
        
        <div v-else-if="filteredAttacks.length === 0" class="text-center p-4">
          <p>No attacks found. Create your first jailbreak attack!</p>
        </div>
        
        <div v-else>
          <DataTable :value="filteredAttacks" responsiveLayout="scroll" stripedRows 
                    :paginator="true" :rows="rows"
                    paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown JumpToPageInput"
                    :rowsPerPageOptions="[5, 10, 20, 50]"
                    currentPageReportTemplate="Showing {first} to {last} of {totalRecords}"
                    :filters="filters" filterDisplay="menu"
                    v-model:selection="selectedAttacks"
                    :globalFilterFields="['name']">
            <Column selectionMode="multiple" headerStyle="width: 3rem">
              <template #header>
                <div class="select-all-container">
                  <Checkbox v-model="selectAll" binary @change="toggleSelectAll" />
                </div>
              </template>
            </Column>
            <Column field="name" header="Name" sortable></Column>
            <Column field="algorithm_type" header="Algorithm Type" sortable></Column>
            <Column field="description" header="Description">
              <template #body="slotProps">
                <div class="description-cell">
                  {{ slotProps.data.description || 'No description' }}
                </div>
              </template>
            </Column>
            <Column header="Actions">
              <template #body="slotProps">
                <div class="btn-group">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-sm" 
                          @click="editAttack(slotProps.data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" 
                          @click="confirmDeleteAttack(slotProps.data)" />
                  <Button icon="pi pi-bolt" class="p-button-text p-button-sm p-button-warning" 
                          @click="executeAttack(slotProps.data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
    
    <!-- Create/Edit Attack Dialog -->
    <Dialog v-model:visible="attackDialog" :header="editMode ? 'Edit Attack' : 'Create New Attack'" 
            :style="{width: '500px'}" :modal="true" class="p-fluid">
      <div class="form-group">
        <label for="name">Name*</label>
        <InputText id="name" v-model.trim="attack.name" required autofocus 
                  :class="{'p-invalid': submitted && !attack.name}" />
        <small class="p-error" v-if="submitted && !attack.name">Name is required.</small>
      </div>
      
      <div class="form-group">
        <label for="algorithm_type">Algorithm Type*</label>
        <Dropdown id="algorithm_type" v-model="attack.algorithm_type" :options="algorithmTypes" 
                 optionLabel="name" optionValue="value" placeholder="Select an algorithm type" 
                 :class="{'p-invalid': submitted && !attack.algorithm_type}" />
        <small class="p-error" v-if="submitted && !attack.algorithm_type">Algorithm type is required.</small>
      </div>
      
      <div class="form-group">
        <label for="description">Description</label>
        <Textarea id="description" v-model="attack.description" rows="5" />
      </div>
      
      <div class="form-group" v-if="attack.algorithm_type === 'template_based'">
        <label for="template_type">Template Type</label>
        <Dropdown id="template_type" v-model="attack.parameters.template_type" :options="templateTypes" 
                 optionLabel="name" optionValue="value" placeholder="Select a template type" />
      </div>
      
      <div class="form-group" v-if="attack.algorithm_type === 'character_stuffing'">
        <label for="char">Character</label>
        <InputText id="char" v-model="attack.parameters.char" placeholder="Character to repeat" />
        
        <label for="num_chars" class="mt-3">Number of Characters</label>
        <InputText id="num_chars" v-model.number="attack.parameters.num_chars" type="number" min="1" />
      </div>
      
      <div class="form-group" v-if="attack.algorithm_type === 'multi_language'">
        <label for="languages">Languages</label>
        <MultiSelect id="languages" v-model="attack.parameters.languages" :options="languageOptions" 
                    optionLabel="name" placeholder="Select languages" display="chip" />
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="saveAttack" />
      </template>
    </Dialog>
    
    <!-- Delete Attack Confirmation Dialog -->
    <Dialog v-model:visible="deleteAttackDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete this attack?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deleteAttackDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-text" @click="deleteAttack" />
      </template>
    </Dialog>
    
    <!-- 批量删除确认对话框 -->
    <Dialog v-model:visible="deleteAttacksDialog" :style="{width: '450px'}" header="确认删除" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>确定要删除选中的 {{ selectedAttacks.length }} 个攻击吗？</span>
      </div>
      <template #footer>
        <Button label="取消" icon="pi pi-times" class="p-button-text" @click="deleteAttacksDialog = false" />
        <Button label="确定删除" icon="pi pi-check" class="p-button-danger p-button-text" @click="deleteSelectedAttacks" />
      </template>
    </Dialog>
    
    <Toast />
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';

export default {
  name: 'AttacksView',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    // Data
    const attacks = ref([]);
    const attack = ref({
      name: '',
      description: '',
      algorithm_type: '',
      parameters: {}
    });
    const selectedAttacks = ref([]);
    const attackDialog = ref(false);
    const deleteAttackDialog = ref(false);
    const deleteAttacksDialog = ref(false);
    const submitted = ref(false);
    const editMode = ref(false);
    const loading = ref(true);
    const selectedAlgorithmType = ref(null);
    const rows = ref(10);
    const selectAll = ref(false);
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    });
    
    // Algorithm types
    const algorithmTypes = [
      { name: 'Template Based', value: 'template_based' },
      { name: 'Character Stuffing', value: 'character_stuffing' },
      { name: 'Multi-language', value: 'multi_language' },
      { name: 'Custom', value: 'custom' }
    ];
    
    const algorithmTypeOptions = computed(() => {
      return [{ name: 'All Types', value: null }, ...algorithmTypes];
    });
    
    // Template types
    const templateTypes = [
      { name: 'DAN (Do Anything Now)', value: 'dan' },
      { name: 'DUDE (Developer Unleashed, Do Everything)', value: 'dude' },
      { name: 'STAN (Strive To Avoid Norms)', value: 'stan' },
      { name: 'KEVIN (Knowledgeable Entity Violating Imposed Norms)', value: 'kevin' }
    ];
    
    // Language options
    const languageOptions = [
      { name: 'Chinese', value: 'zh' },
      { name: 'Spanish', value: 'es' },
      { name: 'Arabic', value: 'ar' },
      { name: 'Russian', value: 'ru' },
      { name: 'Japanese', value: 'ja' },
      { name: 'Korean', value: 'ko' },
      { name: 'French', value: 'fr' },
      { name: 'German', value: 'de' }
    ];
    
    // Computed
    const filteredAttacks = computed(() => {
      if (!selectedAlgorithmType.value || selectedAlgorithmType.value.value === null) {
        return attacks.value;
      } else {
        return attacks.value.filter(a => a.algorithm_type === selectedAlgorithmType.value.value);
      }
    });
    
    // Methods
    const fetchAttacks = async () => {
      loading.value = true;
      try {
        await store.dispatch('fetchAttacks');
        attacks.value = store.state.attacks;
      } catch (error) {
        console.error('Error fetching attacks:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load attacks',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    // 添加全选/取消全选方法
    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedAttacks.value = [...filteredAttacks.value];
      } else {
        selectedAttacks.value = [];
      }
    };
    
    // 监听选中项变化，更新全选状态
    const updateSelectAllState = () => {
      selectAll.value = 
        filteredAttacks.value.length > 0 && 
        selectedAttacks.value.length === filteredAttacks.value.length;
    };
    
    // 监听selectedAttacks变化
    watch(selectedAttacks, () => {
      updateSelectAllState();
    });
    
    const openNewAttackDialog = () => {
      attack.value = {
        name: '',
        description: '',
        algorithm_type: '',
        parameters: {}
      };
      submitted.value = false;
      editMode.value = false;
      attackDialog.value = true;
    };
    
    const editAttack = (data) => {
      attack.value = { ...data };
      
      // Parse parameters if it's a string
      if (typeof attack.value.parameters === 'string') {
        try {
          attack.value.parameters = JSON.parse(attack.value.parameters);
        } catch (e) {
          attack.value.parameters = {};
        }
      }
      
      submitted.value = false;
      editMode.value = true;
      attackDialog.value = true;
    };
    
    const hideDialog = () => {
      attackDialog.value = false;
      submitted.value = false;
    };
    
    const saveAttack = async () => {
      submitted.value = true;
      
      if (!attack.value.name || !attack.value.algorithm_type) {
        return;
      }
      
      try {
        if (editMode.value) {
          // Update existing attack
          await store.dispatch('updateAttack', {
            attackId: attack.value.id,
            attackData: {
              name: attack.value.name,
              description: attack.value.description,
              algorithm_type: attack.value.algorithm_type,
              parameters: attack.value.parameters
            }
          });
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Attack updated',
            life: 3000
          });
        } else {
          // Create new attack
          await store.dispatch('createAttack', {
            name: attack.value.name,
            description: attack.value.description,
            algorithm_type: attack.value.algorithm_type,
            parameters: attack.value.parameters
          });
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Attack created',
            life: 3000
          });
        }
        
        // Refresh attacks
        await fetchAttacks();
        hideDialog();
      } catch (error) {
        console.error('Error saving attack:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save attack',
          life: 3000
        });
      }
    };
    
    const confirmDeleteAttack = (data) => {
      attack.value = data;
      deleteAttackDialog.value = true;
    };
    
    const deleteAttack = async () => {
      try {
        await store.dispatch('deleteAttack', attack.value.id);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Attack deleted',
          life: 3000
        });
        
        deleteAttackDialog.value = false;
        attack.value = {};
        await fetchAttacks();
      } catch (error) {
        console.error('Error deleting attack:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete attack',
          life: 3000
        });
      }
    };
    
    // 批量删除相关方法
    const confirmDeleteSelectedAttacks = () => {
      if (selectedAttacks.value.length > 0) {
        deleteAttacksDialog.value = true;
      } else {
        toast.add({
          severity: 'warn',
          summary: '警告',
          detail: '请先选择要删除的攻击',
          life: 3000
        });
      }
    };
    
    const deleteSelectedAttacks = async () => {
      try {
        loading.value = true;
        const attackIds = selectedAttacks.value.map(attack => attack.id);
        
        const result = await store.dispatch('batchDeleteAttacks', attackIds);
        
        toast.add({
          severity: 'success',
          summary: '删除成功',
          detail: `已成功删除 ${result.results.deleted} 个攻击${result.results.failed > 0 ? `，${result.results.failed} 个删除失败` : ''}`,
          life: 3000
        });
        
        deleteAttacksDialog.value = false;
        selectedAttacks.value = [];
        selectAll.value = false;
        await fetchAttacks();
      } catch (error) {
        console.error('Error deleting selected attacks:', error);
        toast.add({
          severity: 'error',
          summary: '删除失败',
          detail: '删除攻击时发生错误',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const executeAttack = (data) => {
      router.push({ name: 'ExecuteAttack', params: { id: data.id } });
    };
    
    const filterByAlgorithmType = () => {
      // 重置选择状态
      selectedAttacks.value = [];
      selectAll.value = false;
    };
    
    // Lifecycle hooks
    onMounted(() => {
      fetchAttacks();
    });
    
    return {
      attacks,
      filteredAttacks,
      attack,
      selectedAttacks,
      attackDialog,
      deleteAttackDialog,
      deleteAttacksDialog,
      submitted,
      editMode,
      loading,
      filters,
      algorithmTypes,
      algorithmTypeOptions,
      templateTypes,
      languageOptions,
      selectedAlgorithmType,
      rows,
      selectAll,
      fetchAttacks,
      openNewAttackDialog,
      editAttack,
      hideDialog,
      saveAttack,
      confirmDeleteAttack,
      deleteAttack,
      confirmDeleteSelectedAttacks,
      deleteSelectedAttacks,
      executeAttack,
      filterByAlgorithmType,
      toggleSelectAll
    };
  }
}
</script>

<style scoped>
.attacks-view {
  padding: 1rem;
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-container {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding-right: 2.5rem;
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.filter-dropdown {
  width: 100%;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.description-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.mt-3 {
  margin-top: 1rem;
}

.btn-group {
  display: flex;
  gap: 0.5rem;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 批量操作工具栏样式 */
.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #e9ecef;
}

.selected-count {
  font-weight: 600;
  color: #495057;
}

.bulk-actions-buttons {
  display: flex;
  gap: 0.5rem;
}

.select-all-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

@media screen and (min-width: 768px) {
  .filter-container {
    flex-direction: row;
    align-items: center;
  }
  
  .search-container, .filter-dropdown {
    width: auto;
  }
  
  .filter-dropdown {
    min-width: 200px;
  }
}
</style> 