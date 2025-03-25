<template>
  <div class="prompts-view">
    <div class="page-title">
      <h1>Prompts Management</h1>
      <div class="button-group">
        <Button label="Import CSV" icon="pi pi-upload" class="p-button-secondary mr-2" @click="openImportDialog" />
        <Button label="Add New Prompt" icon="pi pi-plus" @click="openNewPromptDialog" />
      </div>
    </div>
    
    <div class="card">
      <div class="filter-container">
        <div class="search-container">
          <InputText v-model="filters.global.value" placeholder="Search by content..." class="search-input" />
          <i class="pi pi-search search-icon"></i>
        </div>
        <div class="filter-dropdown">
          <Dropdown v-model="selectedCategory" :options="categories" optionLabel="name" 
                    placeholder="Filter by category" @change="filterByCategory" />
        </div>
      </div>
      
      <!-- Add bulk operation toolbar -->
      <div class="bulk-actions" v-if="selectedPrompts.length > 0">
        <span class="selected-count">{{ selectedPrompts.length }} item(s) selected</span>
        <div class="bulk-actions-buttons">
          <Button label="Batch Delete" icon="pi pi-trash" severity="danger" @click="confirmDeleteSelectedPrompts" />
        </div>
      </div>
      
      <DataTable :value="filteredPrompts" :paginator="true" :rows="rows" 
                 :loading="loading" responsiveLayout="scroll"
                 :filters="filters" filterDisplay="menu"
                 v-model:selection="selectedPrompts"
                 :globalFilterFields="['content']"
                 paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown JumpToPageInput"
                 :rowsPerPageOptions="[5, 10, 20, 50]"
                 currentPageReportTemplate="Showing {first} to {last} of {totalRecords}">
        <template #empty>
          <div class="p-text-center">No prompts found.</div>
        </template>
        <template #loading>
          <div class="p-text-center">Loading prompts...</div>
        </template>
        
        <Column selectionMode="multiple" headerStyle="width: 3rem">
          <template #header>
            <div class="select-all-container">
              <Checkbox v-model="selectAll" binary @change="toggleSelectAll" />
            </div>
          </template>
        </Column>
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
        <span>Are you sure you want to delete the selected {{ selectedPrompts.length }} prompts?</span>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="deletePromptsDialog = false" />
        <Button label="Confirm Delete" icon="pi pi-check" class="p-button-danger p-button-text" @click="deleteSelectedPrompts" />
      </template>
    </Dialog>
    
    <!-- Dialog for importing CSV -->
    <Dialog v-model:visible="importDialog" header="Import Prompts from CSV" :style="{width: '500px'}" 
            :modal="true" class="p-fluid">
      <div class="p-field">
        <label for="csvFile">Select CSV File</label>
        <div class="p-inputgroup">
          <input type="file" ref="fileInput" accept=".csv" @change="handleFileSelect" style="display: none" />
          <InputText :value="selectedFileName" readonly placeholder="Choose a CSV file" />
          <Button icon="pi pi-upload" @click="triggerFileInput" />
        </div>
      </div>

      <div class="p-field" v-if="csvHeaders.length > 0">
        <label for="columnSelect">Select Column to Import</label>
        <Dropdown id="columnSelect" v-model="selectedColumn" :options="csvHeaders" 
                  placeholder="Select a column" class="w-full" />
      </div>

      <div class="p-field" v-if="csvHeaders.length > 0">
        <label for="datasetName">Dataset Name</label>
        <InputText id="datasetName" v-model="datasetName" placeholder="e.g., AdvBench" 
                   :class="{'p-invalid': submitted && !datasetName}" />
        <small class="p-error" v-if="submitted && !datasetName">Dataset name is required.</small>
      </div>

      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideImportDialog" />
        <Button label="Import" icon="pi pi-check" class="p-button-text" @click="importPrompts" 
                :disabled="!canImport" />
      </template>
    </Dialog>
    
    <Toast />
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useStore } from 'vuex';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';
import Papa from 'papaparse';

export default {
  name: 'PromptsView',
  
  setup() {
    const store = useStore();
    const toast = useToast();
    const fileInput = ref(null);
    
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
    const importDialog = ref(false);
    const selectedFileName = ref('');
    const csvHeaders = ref([]);
    const selectedColumn = ref(null);
    const datasetName = ref('');
    const csvData = ref(null);
    const rows = ref(10);
    const selectAll = ref(false);
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    });
    
    // Computed
    const dialogTitle = ref('');
    const canImport = computed(() => {
      return selectedFileName.value && selectedColumn.value && datasetName.value;
    });
    
    // Add computed property to handle filtering
    const filteredPrompts = computed(() => {
      if (!selectedCategory.value || selectedCategory.value.name === 'All') {
        return prompts.value;
      } else {
        return prompts.value.filter(p => p.category === selectedCategory.value.name);
      }
    });
    
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
    
    // Add select/deselect all method
    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedPrompts.value = [...filteredPrompts.value];
      } else {
        selectedPrompts.value = [];
      }
    };
    
    // Watch for selected items changes, update select all state
    const updateSelectAllState = () => {
      selectAll.value = 
        filteredPrompts.value.length > 0 && 
        selectedPrompts.value.length === filteredPrompts.value.length;
    };
    
    // Watch for selectedPrompts changes
    const watchSelectedPrompts = () => {
      updateSelectAllState();
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
      if (selectedPrompts.value.length > 0) {
        deletePromptsDialog.value = true;
      } else {
        toast.add({
          severity: 'warn',
          summary: 'Warning',
          detail: 'Please select prompts to delete first',
          life: 3000
        });
      }
    };
    
    const deleteSelectedPrompts = async () => {
      try {
        loading.value = true;
        const promptIds = selectedPrompts.value.map(prompt => prompt.id);
        
        const result = await store.dispatch('batchDeletePrompts', promptIds);
        
        toast.add({
          severity: 'success',
          summary: 'Deletion Successful',
          detail: `Successfully deleted ${result.results.deleted} prompts${result.results.failed > 0 ? `, ${result.results.failed} deletion failed` : ''}`,
          life: 3000
        });
        
        deletePromptsDialog.value = false;
        selectedPrompts.value = [];
        selectAll.value = false;
        await fetchPrompts();
      } catch (error) {
        console.error('Error deleting selected prompts:', error);
        toast.add({
          severity: 'error',
          summary: 'Deletion Failed',
          detail: 'An error occurred while deleting prompts',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const filterByCategory = () => {
      // No need to send request to backend, use computed property to filter on frontend
      // Keep this function for additional logic if needed
      selectedPrompts.value = [];
      selectAll.value = false;
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
    
    const openImportDialog = () => {
      importDialog.value = true;
      selectedFileName.value = '';
      csvHeaders.value = [];
      selectedColumn.value = null;
      datasetName.value = '';
      csvData.value = null;
      submitted.value = false;
    };
    
    const hideImportDialog = () => {
      importDialog.value = false;
      selectedFileName.value = '';
      csvHeaders.value = [];
      selectedColumn.value = null;
      datasetName.value = '';
      csvData.value = null;
      submitted.value = false;
    };
    
    const handleFileSelect = (event) => {
      const file = event.target.files[0];
      if (file) {
        selectedFileName.value = file.name;
        Papa.parse(file, {
          complete: (results) => {
            if (results.data && results.data.length > 0) {
              csvHeaders.value = results.data[0].map(header => ({
                name: header,
                value: header
              }));
              csvData.value = results.data.slice(1);
            }
          },
          header: false,
          skipEmptyLines: true
        });
      }
    };
    
    const triggerFileInput = () => {
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.click();
      }
    };
    
    const importPrompts = async () => {
      submitted.value = true;

      if (!canImport.value) {
        return;
      }

      try {
        const prompts = csvData.value
          .filter(row => row[csvHeaders.value.findIndex(h => h.value === selectedColumn.value.value)])
          .map(row => ({
            content: row[csvHeaders.value.findIndex(h => h.value === selectedColumn.value.value)],
            category: datasetName.value
          }));

        for (const prompt of prompts) {
          await store.dispatch('createPrompt', prompt);
        }

        toast.add({
          severity: 'success',
          summary: 'Import Successful',
          detail: `Successfully imported ${prompts.length} data to dataset "${datasetName.value}"`,
          life: 3000
        });

        hideImportDialog();
        await fetchPrompts();
      } catch (error) {
        console.error('Error importing prompts:', error);
        toast.add({
          severity: 'error',
          summary: 'Import Failed',
          detail: 'An error occurred while importing data',
          life: 3000
        });
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      fetchPrompts();
    });
    
    // Watch for selectedPrompts changes
    watch(selectedPrompts, () => {
      watchSelectedPrompts();
    });
    
    return {
      prompts,
      filteredPrompts,
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
      formatDate,
      importDialog,
      hideImportDialog,
      selectedFileName,
      csvHeaders,
      selectedColumn,
      datasetName,
      canImport,
      openImportDialog,
      handleFileSelect,
      triggerFileInput,
      importPrompts,
      rows,
      selectAll,
      toggleSelectAll,
      watchSelectedPrompts
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

.button-group {
  display: flex;
  gap: 0.5rem;
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

.p-field {
  margin-bottom: 1.5rem;
}

.p-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.p-inputgroup {
  display: flex;
  align-items: center;
}

.p-inputgroup .p-button {
  margin-left: -1px;
}

/* Bulk operation toolbar styles */
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