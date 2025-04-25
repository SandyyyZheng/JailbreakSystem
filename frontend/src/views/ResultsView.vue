<template>
  <div class="results-view">
    <div class="page-title">
      <h1>Jailbreak Test Results</h1>
      <Button label="Execute New Attack" icon="pi pi-bolt" @click="navigateToExecuteAttack" />
    </div>
    
    <div class="card">
      <div class="filter-container">
        <div class="search-container">
          <InputText v-model="filters.global.value" placeholder="Search by prompt..." class="search-input" />
          <i class="pi pi-search search-icon"></i>
        </div>
        <div class="filter-dropdowns">
          <div class="filter-dropdown">
            <Dropdown v-model="selectedAttack" :options="attacks" optionLabel="name" 
                      placeholder="Filter by attack" @change="filterByAttack" class="fixed-width-dropdown" />
          </div>
          <div class="filter-dropdown">
            <Dropdown v-model="selectedCategory" :options="categories" optionLabel="name" 
                      placeholder="Filter by dataset" @change="filterByCategory" class="fixed-width-dropdown" />
          </div>
        </div>
      </div>
      
      <!-- Add bulk operation toolbar -->
      <div class="bulk-actions" v-if="selectedResults.length > 0">
        <span class="selected-count">{{ selectedResults.length }} item(s) selected</span>
        <div class="bulk-actions-buttons">
          <Button label="Batch Delete" icon="pi pi-trash" severity="danger" @click="confirmDeleteSelectedResults" />
        </div>
      </div>
      
      <DataTable :value="results" :paginator="true" :rows="rows" 
                 :loading="loading" responsiveLayout="scroll"
                 :filters="filters" filterDisplay="menu"
                 v-model:selection="selectedResults"
                 :globalFilterFields="['original_prompt', 'jailbreak_prompt', 'model_response', 'attack_name']"
                 paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown JumpToPageInput"
                 :rowsPerPageOptions="[5, 10, 20, 50]"
                 currentPageReportTemplate="Showing {first} to {last} of {totalRecords}">
        <template #empty>
          <div class="p-text-center">No results found.</div>
        </template>
        <template #loading>
          <div class="p-text-center">Loading results...</div>
        </template>
        
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        <Column field="id" header="ID" sortable style="width: 5rem"></Column>
        <Column field="attack_name" header="Attack" sortable style="width: 10rem"></Column>
        <Column field="model" header="Model" sortable style="width: 12rem">
          <template #body="slotProps">
            <div>{{ slotProps.data.model || 'Not specified' }}</div>
          </template>
        </Column>
        <Column field="original_prompt" header="Original Prompt" sortable>
          <template #body="slotProps">
            <div class="truncated-text">{{ slotProps.data.original_prompt }}</div>
          </template>
        </Column>
        <Column field="success_rating" header="Harmful Score" sortable style="width: 8rem">
          <template #body="slotProps">
            <div v-if="slotProps.data.success_rating !== null">
              <Rating v-model="slotProps.data.success_rating" :readonly="true" :cancel="false" :stars="5" />
              <span class="ml-2">{{ slotProps.data.success_rating }}/5</span>
            </div>
            <div v-else>Not rated</div>
          </template>
        </Column>
        <Column field="created_at" header="Date" sortable style="width: 10rem">
          <template #body="slotProps">
            {{ formatDate(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column header="Actions" style="width: 10rem">
          <template #body="slotProps">
            <Button icon="pi pi-eye" class="p-button-rounded p-button-info p-mr-2" 
                    @click="viewResult(slotProps.data)" />
            <Button icon="pi pi-trash" class="p-button-rounded p-button-danger" 
                    @click="confirmDeleteResult(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>
    
    <!-- Result Detail Dialog -->
    <Dialog v-model:visible="resultDetailDialog" :header="'Result Details #' + (selectedResult?.id || '')" 
            :style="{width: '80%', maxWidth: '1000px'}" :modal="true">
      <div v-if="selectedResult" class="result-detail">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="detail-section">
              <h3>Attack Information</h3>
              <div class="detail-item">
                <span class="detail-label">Attack Name:</span>
                <span class="detail-value">{{ selectedResult.attack_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Model:</span>
                <span class="detail-value">{{ selectedResult.model || 'Not specified' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Harmful Score:</span>
                <span class="detail-value">
                  <Rating v-model="selectedResult.success_rating" :readonly="true" :cancel="false" :stars="5" />
                  {{ selectedResult.success_rating }}/5
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Date:</span>
                <span class="detail-value">{{ formatDate(selectedResult.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="detail-section">
              <h3>Edit Harmful Score</h3>
              <div class="p-field">
                <label for="model">Model Name</label>
                <div class="p-inputgroup mb-3">
                  <InputText id="model" v-model="editedModel" placeholder="Enter model name" class="w-full" />
                </div>
                
                <label for="rating">Harmful Score (1-5)</label>
                <div class="p-inputgroup mb-3">
                  <Rating v-model="editedRating" :cancel="false" :stars="5" />
                  <span class="ml-2">{{ editedRating }}/5</span>
                </div>
                <div class="p-field-slider mb-3">
                  <label>Adjust Score:</label>
                  <Slider v-model="editedRating" :min="1" :max="5" :step="1" class="w-full" />
                </div>
                <div class="p-field-numeric mb-3">
                  <label>Or enter score directly (1-5):</label>
                  <div class="p-inputgroup">
                    <InputText v-model.number="editedRating" type="number" min="1" max="5" />
                  </div>
                </div>
                <div class="mt-3">
                  <Button label="Update" icon="pi pi-check" class="p-button-primary" @click="updateRating" />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <TabView>
          <TabPanel header="Original Prompt">
            <div class="prompt-container">
              <div class="copy-button-container">
                <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                        @click="copyToClipboard(selectedResult.original_prompt)" />
              </div>
              <div class="prompt-display">
                {{ selectedResult.original_prompt }}
              </div>
            </div>
          </TabPanel>
          
          <TabPanel header="Jailbreak Prompt">
            <div class="prompt-container">
              <div class="copy-button-container">
                <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                        @click="copyToClipboard(selectedResult.jailbreak_prompt)" />
              </div>
              <div class="prompt-display jailbreak-prompt">
                {{ selectedResult.jailbreak_prompt }}
              </div>
            </div>
          </TabPanel>
          
          <TabPanel header="Model Response" v-if="selectedResult.model_response">
            <div class="prompt-container">
              <div class="copy-button-container">
                <Button icon="pi pi-copy" class="p-button-rounded p-button-text copy-button" 
                        @click="copyToClipboard(selectedResult.model_response)" />
              </div>
              <div class="prompt-display model-response">
                {{ selectedResult.model_response }}
              </div>
            </div>
          </TabPanel>
        </TabView>
      </div>
    </Dialog>
    
    <!-- Delete Result Confirmation Dialog -->
    <Dialog v-model:visible="deleteResultDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle p-mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete this result?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deleteResultDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-text" @click="deleteResult" />
      </template>
    </Dialog>
    
    <!-- Batch delete confirmation dialog -->
    <Dialog v-model:visible="deleteResultsDialog" :style="{width: '450px'}" header="Confirm Deletion" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle p-mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete the selected {{ selectedResults.length }} result(s)?</span>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="deleteResultsDialog = false" />
        <Button label="Delete" icon="pi pi-check" class="p-button-danger p-button-text" @click="deleteSelectedResults" />
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
  name: 'ResultsView',
  
  setup() {
    const store = useStore();
    const router = useRouter();
    const toast = useToast();
    
    // Data
    const results = ref([]);
    const attacks = ref([]);
    const categories = ref([]);
    const selectedAttack = ref(null);
    const selectedCategory = ref(null);
    const selectedResult = ref(null);
    const editedRating = ref(0);
    const editedModel = ref('');
    const loading = ref(true);
    const resultDetailDialog = ref(false);
    const deleteResultDialog = ref(false);
    const deleteResultsDialog = ref(false);
    const rows = ref(10);
    const selectedResults = ref([]);
    const selectAll = ref(false);
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    });
    
    // Methods
    const fetchResults = async (attackId = null, category = null) => {
      loading.value = true;
      try {
        await store.dispatch('fetchResults', { attackId, category });
        results.value = store.state.results;
      } catch (error) {
        console.error('Error fetching results:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load results',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const fetchAttacks = async () => {
      try {
        await store.dispatch('fetchAttacks');
        attacks.value = [{ id: null, name: 'All Attacks' }, ...store.state.attacks];
      } catch (error) {
        console.error('Error fetching attacks:', error);
      }
    };
    
    const fetchCategories = async () => {
      try {
        // Get unique categories from all results
        const uniqueCategories = [...new Set(results.value
          .map(result => result.category)
          .filter(Boolean))];
        
        categories.value = [
          { name: 'All Datasets', value: null },
          ...uniqueCategories.map(category => ({ name: category, value: category }))
        ];
        
        // Ensure selectedCategory has a default value
        if (!selectedCategory.value) {
          selectedCategory.value = categories.value[0];
        }
      } catch (error) {
        console.error('Error processing categories:', error);
      }
    };
    
    const navigateToExecuteAttack = () => {
      router.push('/execute-attack');
    };
    
    const viewResult = (result) => {
      selectedResult.value = { ...result };
      editedRating.value = result.success_rating ? Math.min(Math.max(parseInt(result.success_rating), 1), 5) : 5;
      editedModel.value = result.model || '';
      resultDetailDialog.value = true;
    };
    
    const confirmDeleteResult = (result) => {
      selectedResult.value = result;
      deleteResultDialog.value = true;
    };
    
    const deleteResult = async () => {
      try {
        await store.dispatch('deleteResult', selectedResult.value.id);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Result deleted',
          life: 3000
        });
        
        deleteResultDialog.value = false;
        await fetchResults(
          selectedAttack.value?.id,
          selectedCategory.value?.value
        );
      } catch (error) {
        console.error('Error deleting result:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete result',
          life: 3000
        });
      }
    };
    
    const updateRating = async () => {
      if (!selectedResult.value) return;
      
      try {
        await store.dispatch('updateResult', {
          resultId: selectedResult.value.id,
          resultData: {
            success_rating: editedRating.value,
            model: editedModel.value || null
          }
        });
        
        // Update the local data
        selectedResult.value.success_rating = editedRating.value;
        selectedResult.value.model = editedModel.value || null;
        
        // Update the results list
        const index = results.value.findIndex(r => r.id === selectedResult.value.id);
        if (index !== -1) {
          results.value[index].success_rating = editedRating.value;
          results.value[index].model = editedModel.value || null;
        }
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Result updated successfully',
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to update result',
          life: 3000
        });
        console.error('Error updating result:', error);
      }
    };
    
    const filterByAttack = () => {
      const attackId = selectedAttack.value?.id;
      const category = selectedCategory.value?.value;
      
      fetchResults(attackId, category);
      
      // Reset selection state
      selectedResults.value = [];
      selectAll.value = false;
    };
    
    const filterByCategory = () => {
      const attackId = selectedAttack.value?.id;
      const category = selectedCategory.value?.value;
      
      fetchResults(attackId, category);
      
      // Reset selection state
      selectedResults.value = [];
      selectAll.value = false;
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
    
    // Check if there's a result ID in the URL query params
    const checkUrlParams = () => {
      const resultId = router.currentRoute.value.query.id;
      if (resultId) {
        const result = results.value.find(r => r.id === parseInt(resultId));
        if (result) {
          viewResult(result);
        }
      }
    };
    
    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedResults.value = [...results.value];
      } else {
        selectedResults.value = [];
      }
    };
    
    // Listen for selection changes to update selectAll state
    const updateSelectAllState = () => {
      selectAll.value = 
        results.value.length > 0 && 
        selectedResults.value.length === results.value.length;
    };
    
    // Watch for selectedResults changes
    watch(selectedResults, () => {
      updateSelectAllState();
    });
    
    const confirmDeleteSelectedResults = () => {
      if (selectedResults.value.length > 0) {
        deleteResultsDialog.value = true;
      } else {
        toast.add({
          severity: 'warn',
          summary: 'Warning',
          detail: 'Please select results to delete',
          life: 3000
        });
      }
    };
    
    const deleteSelectedResults = async () => {
      try {
        loading.value = true;
        const resultIds = selectedResults.value.map(result => result.id);
        
        const result = await store.dispatch('batchDeleteResults', resultIds);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: `Successfully deleted ${result.results.deleted} result(s)${result.results.failed > 0 ? `, ${result.results.failed} failed` : ''}`,
          life: 3000
        });
        
        deleteResultsDialog.value = false;
        selectedResults.value = [];
        selectAll.value = false;
        
        // Refresh results
        await fetchResults(
          selectedAttack.value?.id,
          selectedCategory.value?.value
        );
      } catch (error) {
        console.error('Error deleting selected results:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'An error occurred while deleting results',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    // Copy to clipboard functionality
    const copyToClipboard = (text) => {
      if (!text) return;
      const tempInput = document.createElement('textarea');
      tempInput.value = text;
      document.body.appendChild(tempInput);
      tempInput.select();
      document.execCommand('copy');
      document.body.removeChild(tempInput);
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Text copied to clipboard',
        life: 3000
      });
    };
    
    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([fetchResults(), fetchAttacks()]);
      await fetchCategories();
      checkUrlParams();
    });
    
    return {
      results,
      attacks,
      categories,
      selectedAttack,
      selectedCategory,
      selectedResult,
      editedRating,
      editedModel,
      loading,
      filters,
      resultDetailDialog,
      deleteResultDialog,
      deleteResultsDialog,
      rows,
      selectedResults,
      selectAll,
      navigateToExecuteAttack,
      viewResult,
      confirmDeleteResult,
      deleteResult,
      updateRating,
      filterByAttack,
      filterByCategory,
      formatDate,
      toggleSelectAll,
      confirmDeleteSelectedResults,
      deleteSelectedResults,
      copyToClipboard
    };
  }
}
</script>

<style scoped>
.results-view {
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
  margin-bottom: 1rem;
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

.filter-dropdowns {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.filter-dropdown {
  width: 100%;
}

/* Fixed dropdown width */
:deep(.fixed-width-dropdown) {
  width: 100%;
}

:deep(.fixed-width-dropdown .p-dropdown-label) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.truncated-text {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-detail {
  padding: 1rem;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-item {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}

.detail-label {
  font-weight: bold;
  margin-right: 0.5rem;
  min-width: 120px;
}

.prompt-container {
  position: relative;
  margin-bottom: 1rem;
}

.copy-button-container {
  position: absolute;
  top: 0.5rem;
  right: 1.5rem; /* Increase right margin to avoid being covered by scrollbar */
  z-index: 10;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}

.prompt-container:hover .copy-button-container {
  opacity: 1;
}

.prompt-display {
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  white-space: pre-wrap;
  font-family: monospace;
  max-height: 400px;
  overflow-y: auto;
}

.jailbreak-prompt {
  background-color: #ffe8e8;
  border: 1px solid #ffcaca;
  /* For ASCII art attacks, need to keep original format and allow horizontal scrolling */
  white-space: pre;
  overflow-x: auto;
  max-width: 100%;
  /* Increase the width of the container for horizontal content */
  min-width: 100%;
}

.model-response {
  background-color: #e8f4ff;
  border: 1px solid #c5e1ff;
}

.copy-button {
  background-color: rgba(255, 255, 255, 0.8) !important;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
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
    justify-content: space-between;
    align-items: center;
  }
  
  .search-container {
    width: 21%;
    margin-bottom: 0;
  }
  
  .filter-dropdowns {
    flex-direction: row;
    width: auto;
    gap: 0.5rem;
  }
  
  .filter-dropdown {
    width: auto;
  }
  
  /* Fixed dropdown width for desktop view */
  :deep(.fixed-width-dropdown) {
    width: 180px !important;
  }
}
</style> 