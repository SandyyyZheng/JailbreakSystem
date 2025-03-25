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
          <span class="selected-count">{{ selectedAttacks.length }} item(s) selected</span>
          <div class="bulk-actions-buttons">
            <Button label="Batch Delete" icon="pi pi-trash" severity="danger" @click="confirmDeleteSelectedAttacks" />
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
            <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
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
        <label for="languages">Language*</label>
        <Dropdown id="language" v-model="attack.parameters.language" :options="languageOptions" 
                 optionLabel="name" optionValue="value" placeholder="Select a language" 
                 :class="{'p-invalid': submitted && !attack.parameters.language}" />
        <small class="p-error" v-if="submitted && !attack.parameters.language">Language is required.</small>
      </div>
      
      <div class="form-group" v-if="attack.algorithm_type === 'token_limit'">
        <label for="filler_text">Filler Text (Optional)</label>
        <Textarea id="filler_text" v-model="attack.parameters.filler_text" rows="3" 
                 placeholder="Leave empty to use default filler text" />
        
        <label for="repeat" class="mt-3">Repeat Count</label>
        <InputText id="repeat" v-model.number="attack.parameters.repeat" type="number" min="1" />
      </div>
      
      <!-- JSON Injection doesn't require additional parameters -->
      <div class="form-group" v-if="attack.algorithm_type === 'json_injection'">
        <div class="p-text-secondary">
          <i class="pi pi-info-circle mr-2"></i>
          JSON Injection attack doesn't require additional parameters.
        </div>
      </div>
      
      <!-- ASCII Art 参数设置 -->
      <div class="form-group" v-if="attack.algorithm_type === 'ascii_art'">
        <label for="ascii_style">ASCII Art Style</label>
        <Dropdown id="ascii_style" v-model="attack.parameters.style" :options="asciiArtStyleOptions" 
                 optionLabel="name" optionValue="value" placeholder="Select an ASCII art style" />
        
        <div class="mt-3">
          <label for="detect_sensitive" class="mr-2">Auto-detect Sensitive Words</label>
          <InputSwitch id="detect_sensitive" v-model="attack.parameters.detect_sensitive" />
          <small class="block mt-1">
            When enabled, the system will automatically identify and mask sensitive words in the prompt.
          </small>
        </div>
      </div>
      
      <!-- CipherChat密码学攻击参数设置 -->
      <div class="form-group" v-if="attack.algorithm_type === 'cipher'">
        <label for="cipher_type">Cipher Type</label>
        <Dropdown id="cipher_type" v-model="attack.parameters.cipher_type" :options="cipherTypeOptions" 
                 optionLabel="name" optionValue="value" placeholder="Select a cipher type" />
        
        <div class="mt-3">
          <label for="use_demonstrations" class="mr-2">Use Demonstrations</label>
          <InputSwitch id="use_demonstrations" v-model="attack.parameters.use_demonstrations" />
          <small class="block mt-1">
            When enabled, the system will include example demonstrations with the encoded content.
          </small>
        </div>
        
        <div class="mt-3">
          <label for="system_prompt">Custom System Prompt (Optional)</label>
          <Textarea id="system_prompt" v-model="attack.parameters.system_prompt" rows="3" 
                   placeholder="Leave empty to use default system prompt" />
          <small class="block mt-1">
            If provided, this will override the default system prompt for the selected cipher.
          </small>
        </div>
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
    <Dialog v-model:visible="deleteAttacksDialog" :style="{width: '450px'}" header="Confirm Delete" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete the selected {{ selectedAttacks.length }} attacks?</span>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="deleteAttacksDialog = false" />
        <Button label="Confirm Delete" icon="pi pi-check" class="p-button-danger p-button-text" @click="deleteSelectedAttacks" />
      </template>
    </Dialog>
    
    <Toast />
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed, watch, onBeforeUnmount } from 'vue';
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
      { name: 'Token Limit', value: 'token_limit' },
      { name: 'JSON Injection', value: 'json_injection' },
      { name: 'ASCII Art', value: 'ascii_art' },
      { name: 'Cipher', value: 'cipher' },
      { name: 'Custom', value: 'custom' }
    ];
    
    const algorithmTypeOptions = computed(() => {
      return [{ name: 'All Types', value: null }, ...algorithmTypes];
    });
    
    // Template types
    const templateTypes = [
      { name: 'Ignore Instructions', value: 'ignore_instructions' },
      { name: 'Hypothetical Scenario', value: 'hypothetical' },
      { name: 'RogueGPT Roleplay', value: 'roleplay' },
      { name: 'Developer Mode', value: 'developer_mode' },
      { name: 'Token Manipulation', value: 'token_manipulation' }
    ];
    
    // ASCII Art style options
    const asciiArtStyleOptions = [
      { name: '5x5 Grid', value: '5x5' },
      { name: 'Block Style', value: 'block' }
    ];
    
    // Cipher type options
    const cipherTypeOptions = [
      { name: 'Caesar Cipher', value: 'caesar' },
      { name: 'Atbash Cipher', value: 'atbash' },
      { name: 'Morse Code', value: 'morse' },
      { name: 'ASCII Code', value: 'ascii' }
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
        parameters: {
          languages: [] // 初始化 languages 数组为空数组
        }
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
      
      // Ensure parameters is always an object
      if (!attack.value.parameters) {
        attack.value.parameters = {};
      }
      
      submitted.value = false;
      editMode.value = true;
      attackDialog.value = true;
    };
    
    const hideDialog = () => {
      attackDialog.value = false;
      submitted.value = false;
      // Reset attack object to prevent stale references
      attack.value = {
        name: '',
        description: '',
        algorithm_type: '',
        parameters: {}
      };
    };
    
    const saveAttack = async () => {
      submitted.value = true;
      
      if (!attack.value.name || !attack.value.algorithm_type) {
        return;
      }
      
      // Ensure parameters is an object
      if (!attack.value.parameters) {
        attack.value.parameters = {};
      }
      
      // 验证必填参数
      if (attack.value.algorithm_type === 'multi_language' && !attack.value.parameters.language) {
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
      attack.value = { ...data };
      
      // Parse parameters if it's a string
      if (typeof attack.value.parameters === 'string') {
        try {
          attack.value.parameters = JSON.parse(attack.value.parameters);
        } catch (e) {
          attack.value.parameters = {};
        }
      }
      
      // Ensure parameters is always an object
      if (!attack.value.parameters) {
        attack.value.parameters = {};
      }
      
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
          summary: 'Warning',
          detail: 'Please select attacks to delete',
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
          summary: 'Delete Successful',
          detail: `Successfully deleted ${result.results.deleted} attacks${result.results.failed > 0 ? `, ${result.results.failed} deletion failed` : ''}`,
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
          summary: 'Delete Failed',
          detail: 'An error occurred while deleting attacks',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const executeAttack = (data) => {
      router.push({ name: 'execute-attack', query: { id: data.id } });
    };
    
    const filterByAlgorithmType = () => {
      // 重置选择状态
      selectedAttacks.value = [];
      selectAll.value = false;
    };
    
    // Watch for algorithm_type changes to initialize appropriate parameters
    watch(() => attack.value.algorithm_type, (newType, oldType) => {
      // Ensure parameters is an object
      if (typeof attack.value.parameters === 'string') {
        try {
          attack.value.parameters = JSON.parse(attack.value.parameters);
        } catch (e) {
          attack.value.parameters = {};
        }
      }
      
      if (!attack.value.parameters) {
        attack.value.parameters = {};
      }
      
      // If algorithm type changed, reset parameters to avoid conflicts
      if (oldType && newType !== oldType) {
        attack.value.parameters = {};
      }
      
      // Initialize parameters based on algorithm type
      if (newType === 'template_based') {
        attack.value.parameters = {
          template_type: attack.value.parameters.template_type || ''
        };
      } else if (newType === 'character_stuffing') {
        attack.value.parameters = {
          char: attack.value.parameters.char || '.',
          num_chars: attack.value.parameters.num_chars || 300
        };
      } else if (newType === 'multi_language') {
        attack.value.parameters = {
          language: attack.value.parameters.language || ''
        };
      } else if (newType === 'token_limit') {
        attack.value.parameters = {
          filler_text: attack.value.parameters.filler_text || '',
          repeat: attack.value.parameters.repeat || 10
        };
      } else if (newType === 'json_injection') {
        // JSON Injection doesn't need parameters
        attack.value.parameters = {};
      } else if (newType === 'ascii_art') {
        attack.value.parameters = {
          style: attack.value.parameters.style || 'block',
          detect_sensitive: attack.value.parameters.detect_sensitive !== undefined ? attack.value.parameters.detect_sensitive : true
        };
      } else if (newType === 'cipher') {
        attack.value.parameters = {
          cipher_type: attack.value.parameters.cipher_type || 'caesar',
          use_demonstrations: attack.value.parameters.use_demonstrations !== undefined ? attack.value.parameters.use_demonstrations : true,
          system_prompt: attack.value.parameters.system_prompt || ''
        };
      } else {
        // For other algorithm types, just ensure parameters is an empty object
        attack.value.parameters = {};
      }
    });
    
    // Lifecycle hooks
    onMounted(() => {
      fetchAttacks();
    });
    
    // Clean up when component is unmounted
    onBeforeUnmount(() => {
      // Close any open dialogs to prevent DOM-related errors
      attackDialog.value = false;
      deleteAttackDialog.value = false;
      deleteAttacksDialog.value = false;
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
      asciiArtStyleOptions,
      cipherTypeOptions,
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