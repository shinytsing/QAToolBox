// app.js
App({
  globalData: {
    userInfo: null,
    token: null,
    baseUrl: 'https://your-api-domain.com/api/v1',
    version: '1.0.0'
  },

  onLaunch() {
    console.log('QAToolBox 小程序启动')
    this.checkLogin()
  },

  onShow() {
    console.log('QAToolBox 小程序显示')
  },

  onHide() {
    console.log('QAToolBox 小程序隐藏')
  },

  onError(error) {
    console.error('小程序错误:', error)
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
      this.getUserInfo()
    }
  },

  // 获取用户信息
  getUserInfo() {
    if (!this.globalData.token) return

    wx.request({
      url: `${this.globalData.baseUrl}/auth/profile/`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.globalData.userInfo = res.data.data
        }
      },
      fail: (error) => {
        console.error('获取用户信息失败:', error)
        this.logout()
      }
    })
  },

  // 登录
  login(token, userInfo) {
    this.globalData.token = token
    this.globalData.userInfo = userInfo
    wx.setStorageSync('token', token)
    wx.setStorageSync('userInfo', userInfo)
  },

  // 登出
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    wx.reLaunch({
      url: '/pages/login/login'
    })
  },

  // 显示加载中
  showLoading(title = '加载中...') {
    wx.showLoading({
      title: title,
      mask: true
    })
  },

  // 隐藏加载中
  hideLoading() {
    wx.hideLoading()
  },

  // 显示提示
  showToast(title, icon = 'none') {
    wx.showToast({
      title: title,
      icon: icon,
      duration: 2000
    })
  },

  // 显示确认对话框
  showConfirm(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title: title,
        content: content,
        success: (res) => {
          resolve(res.confirm)
        }
      })
    })
  }
})
