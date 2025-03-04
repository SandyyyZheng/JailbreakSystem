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
        
        <div v-if="loading" class="loading-container">
          <ProgressSpinner />
        </div>
        
        <div v-else-if="filteredAttacks.length === 0" class="text-center p-4">
          <p>No attacks found. Create your first jailbreak attack!</p>
        </div>
        
        <div v-else>
          <DataTable :value="filteredAttacks" responsiveLayout="scroll" stripedRows 
                    :paginator="filteredAttacks.length > 10" :rows="10" 
                    paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
                    :rowsPerPageOptions="[5, 10, 20]"
                    :filters="filters" filterDisplay="menu"
                    :globalFilterFields="['name']">
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
        <label for="language">Language</label>
        <Dropdown id="language" v-model="attack.parameters.language" :options="languages" 
                 optionLabel="name" optionValue="value" placeholder="Select a language" />
      </div>
      
      <div class="form-group" v-if="attack.algorithm_type === 'token_limit'">
        <label for="repeat">Repeat Count</label>
        <InputText id="repeat" v-model.number="attack.parameters.repeat" type="number" min="1" />
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="closeDialog" />
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="saveAttack" />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="attack">Are you sure you want to delete <b>{{ attack.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deleteDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-text p-button-danger" @click="deleteAttack" />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { FilterMatchMode } from 'primevue/api'

export default {
  name: 'AttacksView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const toast = useToast()
    
    // State
    const loading = ref(true)
    const attacks = ref([])
    const attackDialog = ref(false)
    const deleteDialog = ref(false)
    const submitted = ref(false)
    const editMode = ref(false)
    const selectedAlgorithmType = ref(null)
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    })
    
    // Form data
    const attack = reactive({
      name: '',
      description: '',
      algorithm_type: null,
      parameters: {}
    })
    
    // Algorithm types
    const algorithmTypes = [
      { name: 'Template Based', value: 'template_based' },
      { name: 'Character Stuffing', value: 'character_stuffing' },
      { name: 'Multi-Language', value: 'multi_language' },
      { name: 'Token Limit', value: 'token_limit' },
      { name: 'JSON Injection', value: 'json_injection' }
    ]
    
    // Algorithm type options for filtering (with "All" option)
    const algorithmTypeOptions = computed(() => {
      return [
        { name: 'All Types', value: null },
        ...algorithmTypes
      ]
    })
    
    // Filtered attacks based on selected algorithm type
    const filteredAttacks = computed(() => {
      if (!selectedAlgorithmType.value || selectedAlgorithmType.value.value === null) {
        return attacks.value
      } else {
        return attacks.value.filter(a => a.algorithm_type === selectedAlgorithmType.value.value)
      }
    })
    
    // Template types
    const templateTypes = [
      { name: 'Ignore Instructions', value: 'ignore_instructions' },
      { name: 'Hypothetical Scenario', value: 'hypothetical' },
      { name: 'Roleplay', value: 'roleplay' },
      { name: 'Developer Mode', value: 'developer_mode' },
      { name: 'Token Manipulation', value: 'token_manipulation' }
    ]
    
    // Languages
    const languages = [
      { name: 'Chinese', value: 'chinese' },
      { name: 'Spanish', value: 'spanish' },
      { name: 'French', value: 'french' },
      { name: 'German', value: 'german' },
      { name: 'Russian', value: 'russian' }
    ]
    
    // Methods
    const fetchAttacks = async () => {
      loading.value = true
      
      try {
        await store.dispatch('fetchAttacks')
        attacks.value = store.state.attacks
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load attacks',
          life: 3000
        })
        console.error('Error fetching attacks:', error)
      } finally {
        loading.value = false
      }
    }
    
    const filterByAlgorithmType = () => {
      // 使用计算属性在前端进行筛选，不需要额外操作
    }
    
    const openNewAttackDialog = () => {
      resetAttackForm()
      editMode.value = false
      attackDialog.value = true
    }
    
    const editAttack = (data) => {
      resetAttackForm()
      
      // Clone the attack data to avoid modifying the original
      attack.id = data.id
      attack.name = data.name
      attack.description = data.description
      attack.algorithm_type = data.algorithm_type
      
      // Parse parameters if they exist
      if (data.parameters) {
        try {
          attack.parameters = typeof data.parameters === 'string' 
            ? JSON.parse(data.parameters) 
            : data.parameters
        } catch (e) {
          attack.parameters = {}
        }
      }
      
      editMode.value = true
      attackDialog.value = true
    }
    
    const confirmDeleteAttack = (data) => {
      resetAttackForm()
      
      attack.id = data.id
      attack.name = data.name
      
      deleteDialog.value = true
    }
    
    const executeAttack = (data) => {
      router.push('/execute-attack')
      
      // Store the selected attack in localStorage for the execute page to use
      localStorage.setItem('selectedAttackId', data.id)
    }
    
    const resetAttackForm = () => {
      attack.id = null
      attack.name = ''
      attack.description = ''
      attack.algorithm_type = null
      attack.parameters = {}
      submitted.value = false
    }
    
    const closeDialog = () => {
      attackDialog.value = false
      submitted.value = false
    }
    
    const saveAttack = async () => {
      submitted.value = true
      
      if (!attack.name || !attack.algorithm_type) {
        return
      }
      
      try {
        if (editMode.value) {
          await store.dispatch('updateAttack', {
            attackId: attack.id,
            attackData: {
              name: attack.name,
              description: attack.description,
              algorithm_type: attack.algorithm_type,
              parameters: attack.parameters
            }
          })
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Attack updated successfully',
            life: 3000
          })
        } else {
          await store.dispatch('createAttack', {
            name: attack.name,
            description: attack.description,
            algorithm_type: attack.algorithm_type,
            parameters: attack.parameters
          })
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Attack created successfully',
            life: 3000
          })
        }
        
        attackDialog.value = false
        fetchAttacks()
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: editMode.value ? 'Failed to update attack' : 'Failed to create attack',
          life: 3000
        })
        console.error('Error saving attack:', error)
      }
    }
    
    const deleteAttack = async () => {
      try {
        await store.dispatch('deleteAttack', attack.id)
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Attack deleted successfully',
          life: 3000
        })
        
        deleteDialog.value = false
        fetchAttacks()
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete attack',
          life: 3000
        })
        console.error('Error deleting attack:', error)
      }
    }
    
    onMounted(() => {
      fetchAttacks()
    })
    
    return {
      loading,
      attacks,
      filteredAttacks,
      attack,
      attackDialog,
      deleteDialog,
      submitted,
      editMode,
      filters,
      algorithmTypes,
      algorithmTypeOptions,
      selectedAlgorithmType,
      templateTypes,
      languages,
      openNewAttackDialog,
      editAttack,
      confirmDeleteAttack,
      executeAttack,
      closeDialog,
      saveAttack,
      deleteAttack,
      filterByAlgorithmType
    }
  }
}
</script>

<style scoped>
.attacks-view {
  padding: 20px;
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

.description-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-group {
  display: flex;
  gap: 0.5rem;
}

.confirmation-content {
  display: flex;
  align-items: center;
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 2rem;
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