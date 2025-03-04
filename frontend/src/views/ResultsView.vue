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
        <div class="filter-dropdown">
          <Dropdown v-model="selectedAttack" :options="attacks" optionLabel="name" 
                    placeholder="Filter by attack" @change="filterByAttack" />
        </div>
      </div>
      
      <DataTable :value="results" :paginator="true" :rows="10" 
                 :loading="loading" responsiveLayout="scroll"
                 :filters="filters" filterDisplay="menu"
                 :globalFilterFields="['original_prompt', 'jailbreak_prompt', 'model_response', 'attack_name']">
        <template #empty>
          <div class="p-text-center">No results found.</div>
        </template>
        <template #loading>
          <div class="p-text-center">Loading results...</div>
        </template>
        
        <Column field="id" header="ID" sortable style="width: 5rem"></Column>
        <Column field="attack_name" header="Attack" sortable style="width: 10rem"></Column>
        <Column field="original_prompt" header="Original Prompt" sortable>
          <template #body="slotProps">
            <div class="truncated-text">{{ slotProps.data.original_prompt }}</div>
          </template>
        </Column>
        <Column field="success_rating" header="Harmful" sortable style="width: 8rem">
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
            <div class="prompt-display">{{ selectedResult.original_prompt }}</div>
          </TabPanel>
          
          <TabPanel header="Jailbreak Prompt">
            <div class="prompt-display jailbreak-prompt">{{ selectedResult.jailbreak_prompt }}</div>
          </TabPanel>
          
          <TabPanel header="Model Response" v-if="selectedResult.model_response">
            <div class="prompt-display model-response">{{ selectedResult.model_response }}</div>
          </TabPanel>
        </TabView>
      </div>
    </Dialog>
    
    <!-- Confirmation dialog for deleting result -->
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
    
    <Toast />
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed } from 'vue';
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
    const selectedAttack = ref(null);
    const selectedResult = ref(null);
    const editedRating = ref(5);
    const loading = ref(true);
    const resultDetailDialog = ref(false);
    const deleteResultDialog = ref(false);
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    });
    
    // Methods
    const fetchResults = async (attackId = null) => {
      loading.value = true;
      try {
        await store.dispatch('fetchResults', attackId);
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
    
    const navigateToExecuteAttack = () => {
      router.push('/execute-attack');
    };
    
    const viewResult = (result) => {
      selectedResult.value = { ...result };
      editedRating.value = result.success_rating ? Math.min(Math.max(parseInt(result.success_rating), 1), 5) : 5;
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
        await fetchResults(selectedAttack.value?.id === null ? null : selectedAttack.value?.id);
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
      try {
        // 确保评分在1-5的范围内
        const validRating = Math.min(Math.max(parseInt(editedRating.value) || 5, 1), 5);
        editedRating.value = validRating;
        
        const updatedResult = await store.dispatch('updateResult', {
          resultId: selectedResult.value.id,
          resultData: {
            success_rating: validRating
          }
        });
        
        console.log('Updated result from server:', updatedResult);
        
        // Update the displayed rating
        selectedResult.value.success_rating = validRating;
        
        // Also update in the results list
        const index = results.value.findIndex(r => r.id === selectedResult.value.id);
        if (index !== -1) {
          results.value[index].success_rating = validRating;
        }
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Score updated',
          life: 3000
        });
      } catch (error) {
        console.error('Error updating rating:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to update score',
          life: 3000
        });
      }
    };
    
    const filterByAttack = () => {
      const attackId = selectedAttack.value?.id === null ? null : selectedAttack.value?.id;
      fetchResults(attackId);
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
    
    // Lifecycle hooks
    onMounted(async () => {
      await Promise.all([fetchResults(), fetchAttacks()]);
      checkUrlParams();
    });
    
    return {
      results,
      attacks,
      selectedAttack,
      selectedResult,
      editedRating,
      loading,
      filters,
      resultDetailDialog,
      deleteResultDialog,
      navigateToExecuteAttack,
      viewResult,
      confirmDeleteResult,
      deleteResult,
      updateRating,
      filterByAttack,
      formatDate
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

.prompt-display {
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 1rem;
  white-space: pre-wrap;
  font-family: monospace;
}

.jailbreak-prompt {
  background-color: #ffe8e8;
  border: 1px solid #ffcaca;
}

.model-response {
  background-color: #e8f4ff;
  border: 1px solid #c5e1ff;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
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