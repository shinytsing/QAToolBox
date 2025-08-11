// 工具模态框管理模块
class ToolModalManager {
  constructor() {
    this.activeModal = null;
    this.init();
  }

  init() {
    this.createModalContainer();
  }

  createModalContainer() {
    const modalContainer = document.createElement('div');
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

  openModal(content, title = '工具') {
    const container = document.getElementById('toolModalContainer');
    const contentDiv = document.getElementById('modalContent');
    
    contentDiv.innerHTML = `
      <h2 style="color: var(--rage-primary, #ff6b35); margin-bottom: 20px;">${title}</h2>
      ${content}
    `;
    
    container.style.display = 'flex';
    this.activeModal = container;
    
    container.addEventListener('click', (e) => {
      if (e.target === container) {
        this.closeModal();
      }
    });
  }

  closeModal() {
    if (this.activeModal) {
      this.activeModal.style.display = 'none';
      this.activeModal = null;
    }
  }
}

// 计划编辑器模块
class PlanEditor {
  constructor() {
    this.currentPlan = null;
    this.init();
  }

  init() {
    this.createEditorContainer();
  }

  createEditorContainer() {
    const editorContainer = document.createElement('div');
    editorContainer.id = 'planEditorContainer';
    editorContainer.className = 'plan-editor-container';
    editorContainer.style.cssText = `
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
    
    editorContainer.innerHTML = `
      <div class="editor-content" style="
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
        <button class="editor-close" onclick="closePlanEditor()" style="
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
        <div id="editorContent"></div>
      </div>
    `;
    
    document.body.appendChild(editorContainer);
  }

  openEditor(planData = null) {
    const container = document.getElementById('planEditorContainer');
    const contentDiv = document.getElementById('editorContent');
    
    this.currentPlan = planData || this.getDefaultPlan();
    
    contentDiv.innerHTML = this.renderEditor();
    container.style.display = 'flex';
    
    // 添加关闭事件
    container.addEventListener('click', (e) => {
      if (e.target === container) {
        this.closeEditor();
      }
    });
  }

  closeEditor() {
    const container = document.getElementById('planEditorContainer');
    if (container) {
      container.style.display = 'none';
    }
  }

  getDefaultPlan() {
    return {
      name: '新训练计划',
      description: '',
      days: [
        { name: '周一', exercises: [] },
        { name: '周二', exercises: [] },
        { name: '周三', exercises: [] },
        { name: '周四', exercises: [] },
        { name: '周五', exercises: [] },
        { name: '周六', exercises: [] },
        { name: '周日', exercises: [] }
      ]
    };
  }

  renderEditor() {
    return `
      <h2 style="color: var(--rage-primary, #ff6b35); margin-bottom: 20px;">训练计划编辑器</h2>
      
      <div style="margin-bottom: 20px;">
        <label style="display: block; margin-bottom: 5px; color: var(--rage-text, #e6e6e6);">计划名称:</label>
        <input type="text" id="planName" value="${this.currentPlan.name}" style="
          width: 100%;
          padding: 10px;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
          border-radius: 6px;
          color: white;
        ">
      </div>
      
      <div style="margin-bottom: 20px;">
        <label style="display: block; margin-bottom: 5px; color: var(--rage-text, #e6e6e6);">计划描述:</label>
        <textarea id="planDescription" rows="3" style="
          width: 100%;
          padding: 10px;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
          border-radius: 6px;
          color: white;
          resize: vertical;
        ">${this.currentPlan.description}</textarea>
      </div>
      
      <div style="margin-bottom: 20px;">
        <h3 style="color: var(--rage-primary, #ff6b35); margin-bottom: 15px;">训练安排</h3>
        <div id="daysContainer">
          ${this.currentPlan.days.map((day, index) => `
            <div class="day-item" style="
              margin-bottom: 15px;
              padding: 15px;
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.2));
              border-radius: 8px;
            ">
              <h4 style="color: var(--rage-primary, #ff6b35); margin-bottom: 10px;">${day.name}</h4>
              <button onclick="showDayDetail(${index})" style="
                background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
                border: none;
                color: #000;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
              ">编辑训练内容</button>
            </div>
          `).join('')}
        </div>
      </div>
      
      <div style="text-align: center; margin-top: 30px;">
        <button onclick="savePlan()" style="
          background: var(--rage-gradient, linear-gradient(135deg, #ff6b35 0%, #f7931e 100%));
          border: none;
          color: #000;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: bold;
          margin-right: 10px;
        ">保存计划</button>
        <button onclick="closePlanEditor()" style="
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid var(--rage-border, rgba(255, 107, 53, 0.3));
          color: var(--rage-text, #e6e6e6);
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
        ">取消</button>
      </div>
    `;
  }
}

// 全局实例
let toolModalManager;
let planEditor;

// 全局函数 - 保持向后兼容
function openToolModal(content, title) {
  if (!toolModalManager) {
    toolModalManager = new ToolModalManager();
  }
  toolModalManager.openModal(content, title);
}

function closeToolModal() {
  if (toolModalManager) {
    toolModalManager.closeModal();
  }
}

function openPlanEditor(planData) {
  if (!planEditor) {
    planEditor = new PlanEditor();
  }
  planEditor.openEditor(planData);
}

function closePlanEditor() {
  if (planEditor) {
    planEditor.closeEditor();
  }
}

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

function addExercise(dayIndex) {
  const exerciseList = document.getElementById(`exercisesList${dayIndex}`);
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
    <button onclick="this.parentElement.remove()" style="
      background: rgba(255, 0, 0, 0.3);
      border: 1px solid rgba(255, 0, 0, 0.5);
      color: #ff6b6b;
      padding: 5px 10px;
      border-radius: 4px;
      cursor: pointer;
      margin-top: 10px;
    ">删除</button>
  `;
  
  exerciseList.appendChild(exerciseDiv);
  
  // 移除"暂无训练项目"的提示
  const noExerciseText = exerciseList.querySelector('p');
  if (noExerciseText) {
    noExerciseText.remove();
  }
}

function savePlan() {
  const planName = document.getElementById('planName').value;
  const planDescription = document.getElementById('planDescription').value;
  
  console.log('保存计划:', { planName, planDescription });
  alert('计划保存成功！');
  closePlanEditor();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  toolModalManager = new ToolModalManager();
  planEditor = new PlanEditor();
});
