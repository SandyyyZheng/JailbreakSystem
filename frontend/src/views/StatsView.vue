<template>
  <div class="stats-view">
    <div class="page-title">
      <h1>Jailbreak Statistics</h1>
    </div>
    
    <div v-if="loading" class="loading-container">
      <ProgressSpinner />
      <span class="ml-2">Loading statistics...</span>
    </div>
    
    <div v-else-if="stats && Object.keys(stats).length > 0">
      <!-- Summary Stats -->
      <div class="grid">
        <div class="col-12 md:col-4">
          <div class="stats-card">
            <div class="stats-icon">
              <i class="pi pi-bolt"></i>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ stats.total_results || 0 }}</div>
              <div class="stats-label">Total Tests</div>
            </div>
          </div>
        </div>
        
        <div class="col-12 md:col-4">
          <div class="stats-card">
            <div class="stats-icon success">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ stats.harmful_results || 0 }}</div>
              <div class="stats-label">Successful Jailbreaks</div>
            </div>
          </div>
        </div>
        
        <div class="col-12 md:col-4">
          <div class="stats-card">
            <div class="stats-icon info">
              <i class="pi pi-percentage"></i>
            </div>
            <div class="stats-content">
              <div class="stats-value">{{ formatPercentage(stats.harmful_rate || 0) }}</div>
              <div class="stats-label">Overall Success Rate</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Category Selector -->
      <div class="card mt-4">
        <div class="category-selector">
          <h2>Filter by Prompt Dataset</h2>
          <div class="p-field">
            <Dropdown v-model="selectedCategory" :options="categories" 
                     optionLabel="name" placeholder="Select a dataset"
                     class="w-full md:w-20rem" />
          </div>
        </div>
      </div>
      
      <!-- Attack Stats -->
      <div class="card mt-4">
        <h2>Attack Performance {{ selectedCategory.name !== 'All' ? '- ' + selectedCategory.name + ' Category' : '(Average across datasets)' }}</h2>
        <div class="grid">
          <div class="col-12 md:col-6">
            <DataTable :value="filteredAttackStats" 
                      responsiveLayout="scroll" 
                      class="p-datatable-sm"
                      :scrollable="true"
                      scrollHeight="300px"
                      :rows="5"
                      :rowsPerPageOptions="[5, 10, 20]">
              <Column field="name" header="Attack Name"></Column>
              <Column field="algorithm_type" header="Type"></Column>
              <Column field="total_attempts" header="Tests"></Column>
              <Column field="avg_harmful_score" header="Avg. HS" style="width: 100px">
                <template #body="slotProps">
                  {{ formatRating(slotProps.data.avg_harmful_score) }}
                </template>
              </Column>
              <Column header="ASR (%)" style="width: 100px">
                <template #body="slotProps">
                  {{ formatPercentage(calculateAttackSuccessRate(slotProps.data)) }}
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="chart-container bar-chart-container">
              <h3 class="chart-title">Attack Success Rate by Attack</h3>
              <Chart type="bar" :data="barChartData" :options="barChartOptions" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Algorithm Type Comparison -->
      <div class="card mt-4">
        <h2 class="chart-title text-left">Algorithm Type Comparison</h2>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="chart-container pie-chart-container bg-light-gray">
              <h3 class="chart-title text-center">Tests by Algorithm Type</h3>
              <Chart type="pie" :data="pieChartData" :options="pieChartOptions" />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="chart-container radar-chart-container bg-light-gray">
              <h3 class="chart-title text-center">Average Harmful Score by Dataset and Algorithm Type</h3>
              <Chart type="radar" :data="radarChartData" :options="radarChartOptions" />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Dataset Comparison (NEW) -->
      <div v-if="categories.length > 1" class="card mt-4">
        <h2 class="chart-title text-left">Dataset Comparison</h2>
        <div class="grid">
          <div class="col-12">
            <div class="chart-container stacked-bar-chart-container">
              <h3 class="chart-title text-center">Attack Success Rate by Dataset</h3>
              <Chart type="bar" :data="categoryComparisonData" :options="categoryComparisonOptions" />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="card p-4 text-center">
      <h3>No statistics available</h3>
      <p>Try executing some jailbreak attacks to generate statistics.</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'StatsView',
  
  setup() {
    const store = useStore();
    
    // Data
    const stats = ref({});
    const loading = ref(true);
    const categories = ref([]);
    const selectedCategory = ref({ name: 'All', value: 'All' });
    
    // 获取当前选择的类别下的攻击统计数据
    const filteredAttackStats = computed(() => {
      if (!stats.value) return [];
      
      // 处理原始数据，按照当前选择的类别过滤
      if (selectedCategory.value.name === 'All') {
        return stats.value.attack_stats || [];
      } else {
        // 从后端数据中获取特定类别的攻击数据
        const categoryStats = stats.value.attack_stats_by_category?.[selectedCategory.value.name];
        return categoryStats || [];
      }
    });
    
    // Methods
    const fetchStats = async () => {
      loading.value = true;
      try {
        const response = await store.dispatch('fetchStats');
        if (response) {
          stats.value = response;
          
          // 设置类别选项
          setupCategoryOptions();
        } else {
          stats.value = {
            total_results: 0,
            harmful_results: 0,
            harmful_rate: 0,
            attack_stats: []
          };
        }
      } catch (error) {
        console.error('Error fetching statistics:', error);
        stats.value = {
          total_results: 0,
          harmful_results: 0,
          harmful_rate: 0,
          attack_stats: []
        };
      } finally {
        loading.value = false;
      }
    };
    
    // 设置类别选项
    const setupCategoryOptions = () => {
      // 首先添加"All"类别
      categories.value = [
        { name: 'All', value: 'All' },
      ];
      
      // 从API结果中添加其他类别
      if (stats.value && stats.value.categories) {
        stats.value.categories.forEach(category => {
          categories.value.push({ name: category, value: category });
        });
      } else {
        // 如果API没有返回类别数据，使用默认类别
        const defaultCategories = ['Illegal', 'Harmful', 'Unethical', 'Offensive'];
        defaultCategories.forEach(category => {
          categories.value.push({ name: category, value: category });
        });
      }
      
      selectedCategory.value = categories.value[0];
    };
    
    const formatPercentage = (value) => {
      return (value * 100).toFixed(1) + '%';
    };
    
    const formatRating = (value) => {
      return value ? value.toFixed(1) : 'N/A';
    };
    
    const calculateAttackSuccessRate = (attack) => {
      if (!attack || !attack.total_attempts) return 0;
      return (attack.harmful_attempts / attack.total_attempts);
    };
    
    // 颜色分配函数
    const getColorsList = () => {
      return [
        '#4f46e5', // 蓝紫色
        '#10b981', // 绿色
        '#f59e0b', // 橙色
        '#ef4444', // 红色
        '#8b5cf6', // 紫色
        '#06b6d4', // 青色
        '#ec4899', // 粉色
        '#6366f1', // 靛蓝色
        '#84cc16', // 鲜绿色
        '#14b8a6', // 蓝绿色
        '#f97316', // 橙红色
        '#8d4de8', // 深紫色
        '#0ea5e9', // 天蓝色
        '#d946ef', // 洋红色
        '#64748b'  // 石板灰色
      ];
    };
    
    // 根据算法类型数量分配适当的颜色
    const assignColorsToTypes = (types) => {
      const allColors = getColorsList();
      
      // 为每个类型分配一个不同的颜色
      return types.map((type, index) => {
        // 确保颜色不会重复，如果超出可用颜色数量则循环使用
        return allColors[index % allColors.length];
      });
    };
    
    // 为类别分配颜色
    const assignColorsByCategory = (categories) => {
      const categoryColors = {};
      const allColors = getColorsList();
      
      categories.forEach((category, index) => {
        if (category !== 'All') {
          categoryColors[category] = allColors[index % allColors.length];
        }
      });
      
      return categoryColors;
    };
    
    // Chart data
    const barChartData = computed(() => {
      if (!filteredAttackStats.value || filteredAttackStats.value.length === 0) {
        return { labels: [], datasets: [{ label: 'Attack Success Rate (%)', backgroundColor: '#4f46e5', data: [] }] };
      }
      
      const labels = filteredAttackStats.value.map(attack => attack.name);
      const harmfulRates = filteredAttackStats.value.map(attack => 
        calculateAttackSuccessRate(attack) * 100
      );
      
      return {
        labels: labels,
        datasets: [
          {
            label: 'Attack Success Rate (%)',
            backgroundColor: '#4f46e5',
            data: harmfulRates
          }
        ]
      };
    });
    
    const barChartOptions = {
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Attack Success Rate (%)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.raw.toFixed(1) + '%';
            }
          }
        }
      }
    };
    
    const pieChartData = computed(() => {
      if (!filteredAttackStats.value || filteredAttackStats.value.length === 0) {
        return { 
          labels: [], 
          datasets: [{ 
            data: [], 
            backgroundColor: getColorsList().slice(0, 5)
          }] 
        };
      }
      
      // Group attacks by algorithm type
      const algorithmTypes = {};
      filteredAttackStats.value.forEach(attack => {
        if (!algorithmTypes[attack.algorithm_type]) {
          algorithmTypes[attack.algorithm_type] = 0;
        }
        algorithmTypes[attack.algorithm_type] += attack.total_attempts || 0;
      });
      
      const labels = Object.keys(algorithmTypes);
      const data = Object.values(algorithmTypes);
      
      return {
        labels: labels,
        datasets: [
          {
            data: data,
            backgroundColor: assignColorsToTypes(labels)
          }
        ]
      };
    });
    
    const pieChartOptions = {
      plugins: {
        legend: {
          position: 'bottom'
        },
        title: {
          display: false,
          text: 'Tests by Algorithm Type'
        }
      }
    };
    
    const radarChartData = computed(() => {
      if (!stats.value || !stats.value.attack_stats_by_category || Object.keys(stats.value.attack_stats_by_category).length === 0) {
        return { 
          labels: [], 
          datasets: [] 
        };
      }
      
      // 获取所有算法类型作为标签
      const algorithmTypes = new Set();
      Object.values(stats.value.attack_stats_by_category).forEach(categoryStats => {
        categoryStats.forEach(attack => {
          if (attack.algorithm_type) {
            algorithmTypes.add(attack.algorithm_type);
          }
        });
      });
      
      const labels = Array.from(algorithmTypes);
      
      // 为每个类别创建一个数据集
      const datasets = [];
      const categoryColors = assignColorsByCategory(
        Object.keys(stats.value.attack_stats_by_category)
      );
      
      // 为每个类别创建数据集
      Object.entries(stats.value.attack_stats_by_category).forEach(([category, categoryStats]) => {
        // 计算该类别下每种算法类型的平均harmful score
        const algorithmScores = {};
        const algorithmCounts = {};
        
        // 初始化
        labels.forEach(type => {
          algorithmScores[type] = 0;
          algorithmCounts[type] = 0;
        });
        
        // 累计分数和计数
        categoryStats.forEach(attack => {
          if (attack.algorithm_type && attack.avg_harmful_score) {
            algorithmScores[attack.algorithm_type] += attack.avg_harmful_score;
            algorithmCounts[attack.algorithm_type] += 1;
          }
        });
        
        // 计算平均值
        const avgScores = labels.map(type => {
          if (algorithmCounts[type] > 0) {
            return algorithmScores[type] / algorithmCounts[type];
          }
          return 0;
        });
        
        // 生成一个随机的透明色
        const color = categoryColors[category];
        const backgroundColor = `rgba(${parseInt(color.slice(1, 3), 16)}, ${parseInt(color.slice(3, 5), 16)}, ${parseInt(color.slice(5, 7), 16)}, 0.2)`;
        
        datasets.push({
          label: category,
          data: avgScores,
          backgroundColor: backgroundColor,
          borderColor: color,
          pointBackgroundColor: color,
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: color
        });
      });
      
      return {
        labels: labels,
        datasets: datasets
      };
    });
    
    const radarChartOptions = {
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 0,
          suggestedMax: 5
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
          align: 'center'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const value = context.raw.toFixed(1);
              return `${label}: ${value}`;
            }
          }
        }
      }
    };
    
    // 添加类别比较图表数据
    const categoryComparisonData = computed(() => {
      if (!stats.value || !stats.value.attack_stats || !stats.value.attack_stats_by_category) {
        return { labels: [], datasets: [] };
      }
      
      // 获取所有攻击名称作为标签
      const attackNames = stats.value.attack_stats.map(attack => attack.name);
      
      // 为每个类别创建一个数据集
      const datasets = [];
      const categoryColors = assignColorsByCategory(
        Object.keys(stats.value.attack_stats_by_category)
      );
      
      // 为每个类别创建数据集
      Object.entries(stats.value.attack_stats_by_category).forEach(([category, categoryStats]) => {
        // 获取该类别下每个攻击的ASR
        const categoryData = attackNames.map(attackName => {
          // 查找该攻击在该类别下的数据
          const attack = categoryStats.find(a => a.name === attackName);
          
          if (attack && attack.total_attempts > 0) {
            return (attack.harmful_attempts / attack.total_attempts) * 100;
          }
          return 0;
        });
        
        datasets.push({
          label: category,
          backgroundColor: categoryColors[category],
          data: categoryData
        });
      });
      
      return {
        labels: attackNames,
        datasets: datasets
      };
    });
    
    const categoryComparisonOptions = {
      scales: {
        x: {
          stacked: false,
          title: {
            display: true,
            text: 'Attack Name'
          }
        },
        y: {
          stacked: false,
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Attack Success Rate (%)'
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + context.raw.toFixed(1) + '%';
            }
          }
        }
      }
    };
    
    // 监听类别变化
    watch(selectedCategory, () => {
      console.log(`Dataset changed to: ${selectedCategory.value.name}`);
    });
    
    // Lifecycle hooks
    onMounted(() => {
      fetchStats();
    });
    
    return {
      stats,
      loading,
      categories,
      selectedCategory,
      filteredAttackStats,
      formatPercentage,
      formatRating,
      calculateAttackSuccessRate,
      getColorsList,
      assignColorsToTypes,
      barChartData,
      barChartOptions,
      pieChartData,
      pieChartOptions,
      radarChartData,
      radarChartOptions,
      categoryComparisonData,
      categoryComparisonOptions
    };
  }
}
</script>

<style scoped>
.stats-view {
  padding: 1rem;
}

.page-title {
  margin-bottom: 1.5rem;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.stats-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  height: 100%;
}

.stats-icon {
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.stats-icon i {
  font-size: 1.5rem;
}

.stats-icon.success {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stats-icon.info {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stats-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
}

.card h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.25rem;
  text-align: center;
}

.category-selector {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .category-selector {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .category-selector h2 {
    margin-bottom: 0;
  }
}

.mt-4 {
  margin-top: 1.5rem;
}

.chart-container {
  position: relative;
}

.bar-chart-container {
  height: 300px;
  width: 100%;
}

.pie-chart-container {
  height: 500px;
  width: 85%;
}

.radar-chart-container {
  height: 500px;
  width: 85%;
}

.stacked-bar-chart-container {
  height: 550px;
  width: 100%;
  margin: 0 auto;
}

.chart-title {
  font-size: 1.25rem;
  text-align: center;
}

.bg-light-gray {
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 5px;
}

.success-rate-bar {
  background-color: #e5e7eb;
  border-radius: 4px;
  height: 20px;
  width: 100%;
  overflow: hidden;
}

.success-rate-fill {
  background-color: #4f46e5;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  min-width: 30px;
}
</style> 