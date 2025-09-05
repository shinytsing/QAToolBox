// pages/fitness/fitness.js
const app = getApp()

Page({
  data: {
    userProfile: null,
    stats: {
      totalWorkouts: 0,
      totalMinutes: 0,
      totalCalories: 0,
      streakDays: 0
    },
    recentWorkouts: [],
    achievements: [],
    goals: {
      weeklyWorkouts: 5,
      weeklyMinutes: 300,
      weeklyCalories: 2000
    },
    currentWeek: {
      workouts: 0,
      minutes: 0,
      calories: 0
    }
  },

  onLoad() {
    console.log('健身页面加载')
    this.loadFitnessData()
  },

  onShow() {
    console.log('健身页面显示')
    this.loadFitnessData()
  },

  onPullDownRefresh() {
    this.loadFitnessData()
    wx.stopPullDownRefresh()
  },

  // 加载健身数据
  loadFitnessData() {
    if (!app.globalData.token) {
      wx.redirectTo({
        url: '/pages/login/login'
      })
      return
    }

    this.loadUserProfile()
    this.loadStats()
    this.loadRecentWorkouts()
    this.loadAchievements()
    this.loadCurrentWeek()
  },

  // 加载用户资料
  loadUserProfile() {
    wx.request({
      url: `${app.globalData.baseUrl}/fitness/profile/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            userProfile: res.data.data
          })
        }
      },
      fail: (error) => {
        console.error('加载用户资料失败:', error)
      }
    })
  },

  // 加载统计数据
  loadStats() {
    wx.request({
      url: `${app.globalData.baseUrl}/fitness/stats/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            stats: res.data.data
          })
        }
      },
      fail: (error) => {
        console.error('加载统计数据失败:', error)
      }
    })
  },

  // 加载最近训练
  loadRecentWorkouts() {
    wx.request({
      url: `${app.globalData.baseUrl}/fitness/workouts/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      data: {
        limit: 5
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            recentWorkouts: res.data.data.results
          })
        }
      },
      fail: (error) => {
        console.error('加载最近训练失败:', error)
      }
    })
  },

  // 加载成就
  loadAchievements() {
    wx.request({
      url: `${app.globalData.baseUrl}/fitness/achievements/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            achievements: res.data.data.results
          })
        }
      },
      fail: (error) => {
        console.error('加载成就失败:', error)
      }
    })
  },

  // 加载本周数据
  loadCurrentWeek() {
    wx.request({
      url: `${app.globalData.baseUrl}/fitness/weekly-stats/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            currentWeek: res.data.data
          })
        }
      },
      fail: (error) => {
        console.error('加载本周数据失败:', error)
      }
    })
  },

  // 开始训练
  onStartWorkout() {
    wx.navigateTo({
      url: '/pages/workout-start/workout-start'
    })
  },

  // 查看训练记录
  onViewWorkouts() {
    wx.navigateTo({
      url: '/pages/workout-list/workout-list'
    })
  },

  // 查看成就
  onViewAchievements() {
    wx.navigateTo({
      url: '/pages/achievement-list/achievement-list'
    })
  },

  // 设置目标
  onSetGoals() {
    wx.navigateTo({
      url: '/pages/goal-setting/goal-setting'
    })
  },

  // 查看详情
  onViewDetail(e) {
    const { type } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/${type}/${type}`
    })
  }
})
