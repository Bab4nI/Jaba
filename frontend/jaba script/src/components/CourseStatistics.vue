<template>
    <div class="course-progress-statistics-container">
      <p class="course-statistics-title">Статистика прохождения курса</p>
      <div class="course-statistics-container">
        <!-- Select component would go here -->
        <slot name="select-component"></slot>
      </div>
      <div class="scorecard-container">
        <div class="grade-summary-container">
          <div class="horizontal-button-group">
            <div class="hierarchical-flex-container">
              <div class="vertical-box-with-hidden-overflow"></div>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-1"></slot>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-2"></slot>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-3"></slot>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-4"></slot>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-5"></slot>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-6"></slot>
            </div>
            <div class="hierarchical-flex-container">
              <slot name="button-7"></slot>
            </div>
          </div>
          
          <!-- Rows would be dynamically rendered here -->
          <div v-for="(row, index) in rows" :key="index" class="row-flex-container">
            <div class="hierarchical-flex-container">
              <slot name="input" :row="row"></slot>
            </div>
            <div v-for="(col, colIndex) in 7" :key="colIndex" class="hierarchical-flex-container">
              <div v-if="row.columns && row.columns[colIndex]" class="vertical-box-with-hidden-overflow">
                <slot name="cell" :row="row" :colIndex="colIndex"></slot>
              </div>
              <div v-else class="vertical-box-with-hidden-overflow"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CourseProgressStatistics',
    props: {
      rows: {
        type: Array,
        default: () => [] // Expected format: [{ columns: [/* cell data */] }, ...]
      }
    }
  }
  </script>
  
  <style scoped>
  .course-progress-statistics-container {
    flex: 0 0 auto;
    padding-top: 12.5px;
    margin-left: 44px;
  }
  
  .course-statistics-title {
    padding: 0;
    margin: 0;
    font: 600 24px Raleway, sans-serif;
    color: #24222f;
  }
  
  .course-statistics-container {
    box-sizing: border-box;
    width: 100%;
    margin-top: 34px;
  }
  
  .scorecard-container {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    margin-top: 48px;
    border-radius: 10px;
  }
  
  .grade-summary-container {
    box-sizing: border-box;
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    width: 889px;
    overflow: hidden;
    background: #f5f9f8;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
  }
  
  .horizontal-button-group {
    box-sizing: border-box;
    display: flex;
    flex: 0 0 auto;
    flex-direction: row;
    align-items: flex-start;
    align-self: stretch;
    justify-content: flex-start;
    overflow: hidden;
    background: #d9d9d9;
  }
  
  .hierarchical-flex-container {
    box-sizing: border-box;
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    align-items: flex-start;
    align-self: stretch;
    justify-content: flex-start;
    background: rgba(255, 255, 255, 0);
    border-left: 1px solid #d9d9d9;
  }
  
  .vertical-box-with-hidden-overflow {
    box-sizing: border-box;
    flex: 0 0 auto;
    align-self: stretch;
    height: 36px;
    overflow: hidden;
  }
  
  .row-flex-container {
    box-sizing: border-box;
    display: flex;
    flex: 0 0 auto;
    flex-direction: row;
    align-items: flex-start;
    align-self: stretch;
    justify-content: flex-start;
    overflow: hidden;
    background: #f5f9f8;
  }
  </style>