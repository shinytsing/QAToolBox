// 健身社区功能模块 - 重构版本
// 确保所有函数都在全局作用域中可用

// ==================== 全局函数定义 ====================

// 创建新帖子
function createNewPost() {
  alert('创建帖子功能即将推出！');
}

// 点赞功能
function toggleLike(postId) {
  if (window.fitnessCommunity) {
    window.fitnessCommunity.toggleLike(postId);
  }
}

// 打开健身社区
function openFitnessCommunity() {
  console.log('打开健身社区');
  // 可以在这里添加导航逻辑
}

// 打开工具模态框
function openToolModal(content, title) {
  // 创建模态框容器
  let modalContainer = document.getElementById('toolModalContainer');
  if (!modalContainer) {
    modalContainer = document.createElement('div');
    modalContainer.id = 'toolModalContainer';
    modalContainer.className = 'modal-container';
    modalContainer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.8);
      display: none;
      z-index: 9999;
      align-items: center;
      justify-content: center;
    `;
    
    modalContainer.innerHTML = `
      <div class="modal-content" style="
        background: var(--rage-bg, #1a1a2e);
        border: 2px solid var(--rage-border, rgba(255, 107, 53, 0.3));
        border-radius: 16px;
        padding: 30px;
        max-width: 90%;
        max-height: 90%;
        overflow-y: auto;
        color: white;
        position: relative;
      ">
        <button class="modal-close" onclick="closeToolModal()" style="
          position: absolute;
          top: 15px;
          right: 20px;
          background: none;
          border: none;
          color: var(--rage-primary, #ff6b35);
          font-size: 24px;
          cursor: pointer;
          z-index: 1000;
        ">&times;</button>
        <div id="modalContent"></div>
      </div>
    `;
    
    document.body.appendChild(modalContainer);
  }

  const contentDiv = document.getElementById('modalContent');
  contentDiv.innerHTML = `
    <h2 style="color: var(--rage-primary, #ff6b35); margin-bottom: 20px;">${title}</h2>
    ${content}
  `;
  
  modalContainer.style.display = 'flex';
  
  // 点击背景关闭
  modalContainer.addEventListener('click', (e) => {
    if (e.target === modalContainer) {
      closeToolModal();
    }
  });
}

// 关闭工具模态框
function closeToolModal() {
  const modalContainer = document.getElementById('toolModalContainer');
  if (modalContainer) {
    modalContainer.style.display = 'none';
  }
}

// 打开计划编辑器
function openPlanEditor(planData) {
  const content = `
    <div style="text-align: center; padding: 40px;">
      <i class="fas fa-dumbbell" style="font-size: 3rem; color: var(--rage-primary, #ff6b35); margin-bottom: 20px;"></i>
      <h3>训练计划编辑器</h3>
      <p style="color: var(--rage-text-muted, #a8a8a8); margin-bottom: 20px;">功能开发中，敬请期待！</p>
      <button onclick="closeToolModal()" style="
        background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
        border: none;
        color: #000;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
      ">关闭</button>
    </div>
  `;
  openToolModal(content, '训练计划编辑器');
}

// 显示每日详情
function showDayDetail(dayIndex) {
  const dayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  const content = `
    <h3 style="color: var(--rage-primary, #ff6b35); margin-bottom: 20px;">${dayNames[dayIndex]} 训练内容</h3>
    
    <div style="margin-bottom: 20px;">
      <button onclick="addExercise(${dayIndex})" style="
        background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
        border: none;
        color: #000;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
      ">添加训练项目</button>
    </div>
    
    <div id="exercisesList${dayIndex}" style="
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 15px;
      min-height: 100px;
    ">
      <p style="color: var(--rage-text-muted, #a8a8a8); text-align: center;">暂无训练项目</p>
    </div>
    
    <div style="text-align: center; margin-top: 20px;">
      <button onclick="closeToolModal()" style="
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
        color: var(--rage-text, #e6e6e6);
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
      ">关闭</button>
    </div>
  `;
  
  openToolModal(content, `${dayNames[dayIndex]} 训练详情`);
}

// 添加训练项目
function addExercise(dayIndex) {
  const exerciseList = document.getElementById(`exercisesList${dayIndex}`);
  if (!exerciseList) return;
  
  const exerciseCount = exerciseList.children.length;
  
  const exerciseDiv = document.createElement('div');
  exerciseDiv.style.cssText = `
    margin-bottom: 15px;
    padding: 15px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.2));
  `;
  
  exerciseDiv.innerHTML = `
    <div style="margin-bottom: 10px;">
      <label style="display: block; margin-bottom: 5px; color: var(--rage-text, #e6e6e6);">训练项目 ${exerciseCount + 1}:</label>
      <input type="text" placeholder="例如: 深蹲" style="
        width: 100%;
        padding: 8px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
        border-radius: 4px;
        color: white;
      ">
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
      <div>
        <label style="display: block; margin-bottom: 5px; color: var(--rage-text, #e6e6e6);">组数:</label>
        <input type="number" placeholder="3" style="
          width: 100%;
          padding: 8px;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
          border-radius: 4px;
          color: white;
        ">
      </div>
      <div>
        <label style="display: block; margin-bottom: 5px; color: var(--rage-text, #e6e6e6);">次数:</label>
        <input type="number" placeholder="12" style="
          width: 100%;
          padding: 8px;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
          border-radius: 4px;
          color: white;
        ">
      </div>
    </div>
  `;
  
  exerciseList.appendChild(exerciseDiv);
  
  // 移除"暂无训练项目"的提示
  const noExerciseText = exerciseList.querySelector('p');
  if (noExerciseText) {
    noExerciseText.remove();
  }
}

// ==================== 健身社区类 ====================

class FitnessCommunity {
  constructor() {
    this.currentFilter = 'all';
    this.posts = [];
    this.init();
  }

  init() {
    this.loadPosts();
    this.bindEvents();
    this.updateStats();
  }

  bindEvents() {
    // 筛选按钮事件
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.currentFilter = e.target.dataset.filter;
        this.filterPosts();
      });
    });

    // 话题点击事件
    document.querySelectorAll('.topic-item').forEach(topic => {
      topic.addEventListener('click', () => {
        this.searchByTopic(topic.textContent);
      });
    });

    // 用户点击事件
    document.querySelectorAll('.user-item').forEach(user => {
      user.addEventListener('click', () => {
        this.viewUserProfile(user);
      });
    });
  }

  loadPosts() {
    // 模拟加载帖子数据
    this.posts = [
      {
        id: 1,
        type: 'checkin',
        user: '健身达人',
        avatar: '💪',
        content: '今天完成了30分钟的有氧训练，感觉超棒！',
        likes: 15,
        comments: 3,
        time: '2小时前',
        image: null
      },
      {
        id: 2,
        type: 'plan',
        user: '力量训练师',
        avatar: '🏋️',
        content: '分享一个增肌训练计划，适合初学者',
        likes: 28,
        comments: 7,
        time: '5小时前',
        image: null
      },
      {
        id: 3,
        type: 'achievement',
        user: '减脂小能手',
        avatar: '🎯',
        content: '坚持健身3个月，成功减重10公斤！',
        likes: 45,
        comments: 12,
        time: '1天前',
        image: null
      }
    ];

    this.renderPosts();
  }

  renderPosts() {
    const postsList = document.getElementById('postsList');
    if (!postsList) return;

    if (this.posts.length === 0) {
      postsList.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--rage-text-muted, #a8a8a8);">
          <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 15px; color: var(--rage-primary, #ff6b35);"></i>
          <h3>还没有帖子</h3>
          <p>成为第一个发布健身分享的人吧！</p>
        </div>
      `;
      return;
    }

    const filteredPosts = this.currentFilter === 'all' 
      ? this.posts 
      : this.posts.filter(post => post.type === this.currentFilter);

    postsList.innerHTML = filteredPosts.map(post => `
      <div class="post-item" style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.2));
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
      " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
          <div style="
            width: 50px;
            height: 50px;
            background: var(--rage-primary, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-right: 15px;
          ">${post.avatar}</div>
          <div>
            <div style="color: var(--rage-text, #e6e6e6); font-weight: 600; margin-bottom: 3px;">${post.user}</div>
            <div style="color: var(--rage-text-muted, #a8a8a8); font-size: 0.9rem;">${post.time}</div>
          </div>
        </div>
        
        <div style="color: var(--rage-text, #e6e6e6); margin-bottom: 15px; line-height: 1.6;">
          ${post.content}
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; gap: 20px;">
            <button onclick="toggleLike(${post.id})" style="
              background: none;
              border: none;
              color: var(--rage-text-muted, #a8a8a8);
              cursor: pointer;
              display: flex;
              align-items: center;
              gap: 5px;
              transition: color 0.3s ease;
            " onmouseover="this.style.color='var(--rage-primary, #ff6b35)'" onmouseout="this.style.color='var(--rage-text-muted, #a8a8a8)'">
              <i class="fas fa-heart"></i>
              <span>${post.likes}</span>
            </button>
            <button onclick="fitnessCommunity.showComments(${post.id})" style="
              background: none;
              border: none;
              color: var(--rage-text-muted, #a8a8a8);
              cursor: pointer;
              display: flex;
              align-items: center;
              gap: 5px;
              transition: color 0.3s ease;
            " onmouseover="this.style.color='var(--rage-primary, #ff6b35)'" onmouseout="this.style.color='var(--rage-text-muted, #a8a8a8)'">
              <i class="fas fa-comment"></i>
              <span>${post.comments}</span>
            </button>
          </div>
          <div style="
            padding: 4px 12px;
            background: rgba(255, 107, 53, 0.2);
            border: 1px solid rgba(255, 107, 53, 0.3);
            border-radius: 20px;
            color: var(--rage-primary, #ff6b35);
            font-size: 0.8rem;
            font-weight: 600;
          ">${this.getTypeLabel(post.type)}</div>
        </div>
      </div>
    `).join('');
  }

  getTypeLabel(type) {
    const labels = {
      'checkin': '打卡分享',
      'plan': '训练计划',
      'video': '训练视频',
      'achievement': '成就分享',
      'question': '健身问答',
      'motivation': '励志分享'
    };
    return labels[type] || '其他';
  }

  filterPosts() {
    this.renderPosts();
  }

  searchByTopic(topic) {
    console.log('搜索话题:', topic);
    // 这里可以实现话题搜索功能
  }

  viewUserProfile(user) {
    console.log('查看用户资料:', user);
    // 这里可以实现用户资料查看功能
  }

  toggleLike(postId) {
    const post = this.posts.find(p => p.id === postId);
    if (post) {
      post.likes += 1;
      this.renderPosts();
    }
  }

  showComments(postId) {
    console.log('显示评论:', postId);
    // 这里可以实现评论显示功能
  }

  updateStats() {
    setTimeout(() => {
      const totalPosts = document.getElementById('totalPosts');
      const totalUsers = document.getElementById('totalUsers');
      const totalLikes = document.getElementById('totalLikes');
      
      if (totalPosts) totalPosts.textContent = this.posts.length;
      if (totalUsers) totalUsers.textContent = '89';
      if (totalLikes) totalLikes.textContent = this.posts.reduce((sum, post) => sum + post.likes, 0);
    }, 1000);
  }
}

// ==================== 初始化代码 ====================

// 全局健身社区实例
let fitnessCommunity;

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  fitnessCommunity = new FitnessCommunity();
  window.fitnessCommunity = fitnessCommunity; // 全局访问
});

// 确保所有函数都在全局作用域中可用
window.createNewPost = createNewPost;
window.toggleLike = toggleLike;
window.openFitnessCommunity = openFitnessCommunity;
window.openToolModal = openToolModal;
window.closeToolModal = closeToolModal;
window.openPlanEditor = openPlanEditor;
window.showDayDetail = showDayDetail;
window.addExercise = addExercise;

// ==================== 辅助函数 ====================

// 显示评论功能
function showComments(postId) {
  const content = `
    <div style="text-align: center; padding: 40px;">
      <i class="fas fa-comments" style="font-size: 3rem; color: var(--rage-primary, #ff6b35); margin-bottom: 20px;"></i>
      <h3>评论功能</h3>
      <p style="color: var(--rage-text-muted, #a8a8a8); margin-bottom: 20px;">评论功能开发中，敬请期待！</p>
      <button onclick="closeToolModal()" style="
        background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
        border: none;
        color: #000;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
      ">关闭</button>
    </div>
  `;
  openToolModal(content, '评论');
}

// 搜索话题功能
function searchByTopic(topic) {
  const content = `
    <div style="text-align: center; padding: 40px;">
      <i class="fas fa-search" style="font-size: 3rem; color: var(--rage-primary, #ff6b35); margin-bottom: 20px;"></i>
      <h3>话题搜索</h3>
      <p style="color: var(--rage-text-muted, #a8a8a8); margin-bottom: 20px;">搜索话题: "${topic}"</p>
      <p style="color: var(--rage-text-muted, #a8a8a8); margin-bottom: 20px;">搜索功能开发中，敬请期待！</p>
      <button onclick="closeToolModal()" style="
        background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
        border: none;
        color: #000;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
      ">关闭</button>
    </div>
  `;
  openToolModal(content, '话题搜索');
}

// 查看用户资料功能
function viewUserProfile(user) {
  const content = `
    <div style="text-align: center; padding: 40px;">
      <i class="fas fa-user" style="font-size: 3rem; color: var(--rage-primary, #ff6b35); margin-bottom: 20px;"></i>
      <h3>用户资料</h3>
      <p style="color: var(--rage-text-muted, #a8a8a8); margin-bottom: 20px;">查看用户: ${user}</p>
      <p style="color: var(--rage-text-muted, #a8a8a8); margin-bottom: 20px;">用户资料功能开发中，敬请期待！</p>
      <button onclick="closeToolModal()" style="
        background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
        border: none;
        color: #000;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
      ">关闭</button>
    </div>
  `;
  openToolModal(content, '用户资料');
}

// 将辅助函数也添加到全局作用域
window.showComments = showComments;
window.searchByTopic = searchByTopic;
window.viewUserProfile = viewUserProfile;

// ==================== 错误处理 ====================

// 全局错误处理
window.addEventListener('error', function(e) {
  console.error('JavaScript错误:', e.error);
  // 可以在这里添加错误上报逻辑
});

// 确保在页面加载完成后所有功能都可用
window.addEventListener('load', function() {
  console.log('健身社区功能已加载完成');
  
  // 检查关键元素是否存在
  const postsList = document.getElementById('postsList');
  if (postsList) {
    console.log('找到帖子列表元素');
  }
  
  // 初始化健身社区（如果还没有初始化）
  if (!window.fitnessCommunity) {
    console.log('重新初始化健身社区');
    window.fitnessCommunity = new FitnessCommunity();
  }
});