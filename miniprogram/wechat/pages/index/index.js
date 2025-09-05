// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    stats: {
      totalWorkouts: 0,
      totalTools: 0,
      totalSocial: 0,
      totalDays: 0
    },
    recentActivities: [],
    quickActions: [
      {
        id: 'fitness',
        name: '健身管理',
        icon: '💪',
        color: '#409eff',
        path: '/pages/fitness/fitness'
      },
      {
        id: 'life',
        name: '生活助手',
        icon: '🌟',
        color: '#67c23a',
        path: '/pages/life/life'
      },
      {
        id: 'geek',
        name: '极客工具',
        icon: '🛠️',
        color: '#e6a23c',
        path: '/pages/geek/geek'
      },
      {
        id: 'social',
        name: '社交娱乐',
        icon: '💬',
        color: '#f56c6c',
        path: '/pages/social/social'
      }
    ]
  },

  onLoad() {
    console.log('首页加载')
    this.loadUserData()
  },

  onShow() {
    console.log('首页显示')
    this.loadUserData()
  },

  onPullDownRefresh() {
    this.loadUserData()
    wx.stopPullDownRefresh()
  },

  // 加载用户数据
  loadUserData() {
    if (!app.globalData.token) {
      wx.redirectTo({
        url: '/pages/login/login'
      })
      return
    }

    this.setData({
      userInfo: app.globalData.userInfo
    })

    this.loadStats()
    this.loadRecentActivities()
  },

  // 加载统计数据
  loadStats() {
    wx.request({
      url: `${app.globalData.baseUrl}/admin/stats/`,
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

  // 加载最近活动
  loadRecentActivities() {
    wx.request({
      url: `${app.globalData.baseUrl}/admin/activities/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${app.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            recentActivities: res.data.data
          })
        }
      },
      fail: (error) => {
        console.error('加载最近活动失败:', error)
      }
    })
  },

  // 快速操作
  onQuickAction(e) {
    const { path } = e.currentTarget.dataset
    wx.navigateTo({
      url: path
    })
  },

  // 查看详情
  onViewDetail(e) {
    const { type } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/${type}/${type}`
    })
  },

  // 刷新数据
  onRefresh() {
    this.loadUserData()
  }
})
