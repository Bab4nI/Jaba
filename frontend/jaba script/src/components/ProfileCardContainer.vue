<template>
    <div style="display: inline-block; width: 1505px">
      <div class="main-content-container1">
        <div class="profile-card-container">
          <div class="main-content-container">
            <div class="profile-card-container1">
              <div class="sidebar-container">
                <div class="course-progress-stats-container">
                  <div class="course-progress-container">
                    <div class="course-progress-container">
                      <!-- PLACEHOLDER - Input Component detected here. Go to "React Code" via right click menu to see code generated -->
                    </div>
                    <div class="course-progress-tracker">
                      <p class="progress-tracker-text-style">Прогресс прохождения курса</p>
                    </div>
                  </div>
                  <p class="course-progress-statistics">Статистика</p>
                </div>
                <p class="progress-indicator-text-style">Выйти из аккаунта</p>
              </div>
              <div class="vertical-divider1"></div>
              <!-- profile container end-->
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>

</script>

<style scoped>
.main-content-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  min-width: 1480px;
  background: #ebefef;
}
.profile-card-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.main-content-container {
  box-sizing: border-box;
  min-width: 1280px;
  padding-top: 84px;
  padding-bottom: 96px;
}

.profile-card-container1 {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 48px;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  padding: 57px 32px 225px;
  background: #f5f9f8;
  border-radius: 30px;
}

.sidebar-container {
  box-sizing: border-box;
  display: flex;
  flex: 0 0 214px;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  padding-top: 24.5px;
}

.course-progress-stats-container {
  flex: 0 0 auto;
}

.course-progress-container {
  box-sizing: border-box;
  width: 100%;
}

.course-progress-tracker {
  padding-right: 19px;
  padding-left: 19px;
  margin-top: 23px;
}

.progress-tracker-text-style {
  box-sizing: border-box;
  max-width: 195px;
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #575667;
  text-align: left;
}

.course-progress-statistics {
  padding: 0;
  padding-right: 17px;
  padding-left: 17px;
  margin: 0;
  margin-top: 36px;
  font: 400 20px Raleway, sans-serif;
  color: #575667;
}

.progress-indicator-text-style {
  padding: 0;
  margin: 0;
  font: 400 20px Raleway, sans-serif;
  color: #575667;
}

.vertical-divider1 {
  flex: 0 0 auto;
  width: 1px;
  height: 100%;
  background: #575667;
}
</style>