<template>
  <div class="prompts-view">
    <div class="page-title">
      <h1>Prompts Management</h1>
      <Button label="Add New Prompt" icon="pi pi-plus" @click="openNewPromptDialog" />
    </div>
    
    <div class="card">
      <div class="p-d-flex p-jc-between p-mb-3">
        <div class="p-input-icon-left">
          <i class="pi pi-search" />
          <InputText v-model="filters.global" placeholder="Search prompts..." />
        </div>
        <Dropdown v-model="selectedCategory" :options="categories" optionLabel="name" 
                  placeholder="Filter by category" class="p-ml-2" @change="filterByCategory" />
      </div>
      
      <DataTable :value="prompts" :paginator="true" :rows="10" 
                 :loading="loading" responsiveLayout="scroll"
                 :filters="filters" filterDisplay="menu"
                 v-model:selection="selectedPrompts"
                 :globalFilterFields="['content', 'category']">
        <template #empty>
          <div class="p-text-center">No prompts found.</div>
        </template>
        <template #loading>
          <div class="p-text-center">Loading prompts...</div>
        </template>
        
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        <Column field="id" header="ID" sortable style="width: 5rem"></Column>
        <Column field="content" header="Prompt Content" sortable>
          <template #body="slotProps">
            <div class="prompt-content">{{ slotProps.data.content }}</div>
          </template>
        </Column>
        <Column field="category" header="Category" sortable style="width: 12rem"></Column>
        <Column field="created_at" header="Created" sortable style="width: 12rem">
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column header="Actions" style="width: 10rem">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="p-button-rounded p-button-success p-mr-2" 
                    @click="editPrompt(slotProps.data)" />
            <Button icon="pi pi-trash" class="p-button-rounded p-button-danger" 
                    @click="confirmDeletePrompt(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>
    
    <!-- Dialog for adding/editing prompts -->
    <Dialog v-model:visible="promptDialog" :header="dialogTitle" :style="{width: '500px'}" 
            :modal="true" class="p-fluid">
      <div class="p-field">
        <label for="content">Prompt Content</label>
        <Textarea id="content" v-model="prompt.content" required rows="5" 
                  :class="{'p-invalid': submitted && !prompt.content}" />
        <small class="p-error" v-if="submitted && !prompt.content">Content is required.</small>
      </div>
      
      <div class="p-field">
        <label for="category">Category</label>
        <div class="p-inputgroup">
          <Dropdown id="category" v-model="prompt.category" :options="categories" optionLabel="name" 
                    placeholder="Select a category" class="w-full" />
          <Button icon="pi pi-plus" @click="showCategoryInput = true" v-if="!showCategoryInput" />
        </div>
      </div>
      
      <div class="p-field" v-if="showCategoryInput">
        <label for="newCategory">New Category</label>
        <div class="p-inputgroup">
          <InputText id="newCategory" v-model="newCategory" placeholder="Enter new category" />
          <Button icon="pi pi-check" @click="addCategory" />
          <Button icon="pi pi-times" class="p-button-danger" @click="showCategoryInput = false" />
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog" />
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="savePrompt" />
      </template>
    </Dialog>
    
    <!-- Confirmation dialog for deleting prompts -->
    <Dialog v-model:visible="deletePromptDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle p-mr-3" style="font-size: 2rem" />
        <span v-if="prompt">Are you sure you want to delete this prompt?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deletePromptDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-text" @click="deletePrompt" />
      </template>
    </Dialog>
    
    <!-- Confirmation dialog for deleting multiple prompts -->
    <Dialog v-model:visible="deletePromptsDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle p-mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete the selected prompts?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deletePromptsDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-text" @click="deleteSelectedPrompts" />
      </template>
    </Dialog>
    
    <Toast />
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue';
import { useStore } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';

export default {
  name: 'PromptsView',
  
  setup() {
    const store = useStore();
    const toast = useToast();
    
    // Data
    const prompts = ref([]);
    const prompt = ref({});
    const selectedPrompts = ref([]);
    const promptDialog = ref(false);
    const deletePromptDialog = ref(false);
    const deletePromptsDialog = ref(false);
    const submitted = ref(false);
    const loading = ref(true);
    const categories = ref([]);
    const selectedCategory = ref(null);
    const showCategoryInput = ref(false);
    const newCategory = ref('');
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    });
    
    // Computed
    const dialogTitle = ref('');
    
    // Methods
    const fetchPrompts = async () => {
      loading.value = true;
      try {
        await store.dispatch('fetchPrompts');
        prompts.value = store.state.prompts;
        
        // Extract unique categories
        const uniqueCategories = [...new Set(prompts.value.map(p => p.category).filter(Boolean))];
        categories.value = uniqueCategories.map(cat => ({ name: cat }));
        
        // Add "All" option
        categories.value.unshift({ name: 'All' });
      } catch (error) {
        console.error('Error fetching prompts:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load prompts',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const openNewPromptDialog = () => {
      prompt.value = {};
      submitted.value = false;
      promptDialog.value = true;
      dialogTitle.value = 'Add New Prompt';
    };
    
    const editPrompt = (data) => {
      prompt.value = { ...data };
      promptDialog.value = true;
      dialogTitle.value = 'Edit Prompt';
    };
    
    const hideDialog = () => {
      promptDialog.value = false;
      submitted.value = false;
      showCategoryInput.value = false;
    };
    
    const savePrompt = async () => {
      submitted.value = true;
      
      if (!prompt.value.content) {
        return;
      }
      
      try {
        if (prompt.value.id) {
          // Update existing prompt
          await store.dispatch('updatePrompt', {
            promptId: prompt.value.id,
            promptData: {
              content: prompt.value.content,
              category: prompt.value.category?.name || prompt.value.category
            }
          });
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Prompt updated',
            life: 3000
          });
        } else {
          // Create new prompt
          await store.dispatch('createPrompt', {
            content: prompt.value.content,
            category: prompt.value.category?.name || prompt.value.category
          });
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Prompt created',
            life: 3000
          });
        }
        
        // Refresh prompts
        await fetchPrompts();
        hideDialog();
      } catch (error) {
        console.error('Error saving prompt:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save prompt',
          life: 3000
        });
      }
    };
    
    const confirmDeletePrompt = (data) => {
      prompt.value = data;
      deletePromptDialog.value = true;
    };
    
    const deletePrompt = async () => {
      try {
        await store.dispatch('deletePrompt', prompt.value.id);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Prompt deleted',
          life: 3000
        });
        
        deletePromptDialog.value = false;
        prompt.value = {};
        await fetchPrompts();
      } catch (error) {
        console.error('Error deleting prompt:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete prompt',
          life: 3000
        });
      }
    };
    
    const confirmDeleteSelectedPrompts = () => {
      deletePromptsDialog.value = true;
    };
    
    const deleteSelectedPrompts = async () => {
      try {
        for (const prompt of selectedPrompts.value) {
          await store.dispatch('deletePrompt', prompt.id);
        }
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Selected prompts deleted',
          life: 3000
        });
        
        deletePromptsDialog.value = false;
        selectedPrompts.value = [];
        await fetchPrompts();
      } catch (error) {
        console.error('Error deleting selected prompts:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete selected prompts',
          life: 3000
        });
      }
    };
    
    const filterByCategory = () => {
      if (selectedCategory.value && selectedCategory.value.name !== 'All') {
        store.dispatch('fetchPrompts', selectedCategory.value.name);
      } else {
        store.dispatch('fetchPrompts');
      }
    };
    
    const addCategory = () => {
      if (newCategory.value) {
        categories.value.push({ name: newCategory.value });
        prompt.value.category = { name: newCategory.value };
        newCategory.value = '';
        showCategoryInput.value = false;
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date);
    };
    
    // Lifecycle hooks
    onMounted(() => {
      fetchPrompts();
    });
    
    return {
      prompts,
      prompt,
      selectedPrompts,
      promptDialog,
      deletePromptDialog,
      deletePromptsDialog,
      submitted,
      loading,
      filters,
      categories,
      selectedCategory,
      showCategoryInput,
      newCategory,
      dialogTitle,
      fetchPrompts,
      openNewPromptDialog,
      editPrompt,
      hideDialog,
      savePrompt,
      confirmDeletePrompt,
      deletePrompt,
      confirmDeleteSelectedPrompts,
      deleteSelectedPrompts,
      filterByCategory,
      addCategory,
      formatDate
    };
  }
}
</script>

<style scoped>
.prompts-view {
  padding: 1rem;
}

.page-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.prompt-content {
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.p-dialog .p-dialog-content {
  padding: 2rem;
}
</style> 