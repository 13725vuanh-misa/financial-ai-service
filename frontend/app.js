/* API integration is intentionally kept in this file so the backend URL has one source of truth. */
const API = { base: () => document.querySelector('#backendUrl').value.trim().replace(/\/$/, '') };

const BUILDERS = [
  ['quarterly_v2_case_a', 'Quarterly V2 · Case A'],
  ['quarterly_v2_case_b', 'Quarterly V2 · Case B'],
  ['quarterly_v2_merged', 'Quarterly V2 · Merged'],
];
const ALGORITHMS = [
  { key:'logistic_regression', name:'Logistic Regression', description:'Hồi quy logistic cho bài toán phân loại.', fields:[['max_iter','Số vòng lặp tối đa','number'],['C','C (regularization)','number']] },
  { key:'decision_tree', name:'Decision Tree', description:'Phân loại dựa trên cây quyết định.', fields:[['max_depth','Độ sâu tối đa','number'],['min_samples_leaf','Mẫu tối thiểu tại lá','number']] },
  { key:'random_forest', name:'Random Forest', description:'Kết hợp nhiều cây quyết định.', fields:[['n_estimators','Số lượng cây','number'],['max_depth','Độ sâu tối đa','number']] },
  { key:'extra_trees', name:'Extra Trees', description:'Cây quyết định với cách chia ngẫu nhiên.', fields:[['n_estimators','Số lượng cây','number'],['max_depth','Độ sâu tối đa','number']] },
  { key:'gradient_boosting', name:'Gradient Boosting', description:'Huấn luyện tuần tự để cải thiện dự đoán.', fields:[['n_estimators','Số lượng cây','number'],['learning_rate','Learning rate','number'],['max_depth','Độ sâu tối đa','number']] },
  { key:'hist_gradient_boosting', name:'Hist Gradient Boosting', description:'Gradient Boosting tối ưu bằng histogram.', fields:[['max_iter','Số vòng lặp tối đa','number'],['learning_rate','Learning rate','number'],['max_leaf_nodes','Số lá tối đa','number']] },
  { key:'knn', name:'K-Nearest Neighbors', description:'Phân loại theo các mẫu gần nhất.', fields:[['n_neighbors','Số láng giềng','number'],['weights','Cách tính trọng số','select', ['uniform','distance']] ] },
  { key:'svm', name:'Support Vector Machine', description:'Tìm ranh giới phân tách tối ưu.', fields:[['C','C (regularization)','number'],['kernel','Kernel','select',['linear','poly','rbf','sigmoid']]] },
];
const METRICS = [['accuracy','Accuracy'],['balanced_accuracy','Balanced Accuracy'],['precision','Precision'],['recall','Recall'],['f1','F1 Score'],['auc','AUC']];
const SPLITS = { walk_forward:{label:'Walk Forward', fields:[['time_col','Cột thời gian','text','quarter'],['min_train_size','Train tối thiểu','number',8],['test_size','Kích thước Test','number',1],['step_size','Bước trượt','number',1]]}, rolling_window:{label:'Rolling Window',fields:[['time_col','Cột thời gian','text','quarter'],['train_size','Kích thước Train','number',8],['test_size','Kích thước Test','number',1],['step_size','Bước trượt','number',1]]}, single_split:{label:'Single Split',fields:[['time_col','Cột thời gian','text','quarter'],['train_size','Kích thước Train','number',9],['test_size','Kích thước Test (tuỳ chọn)','number','']]}};

const state = { datasetMode:'existing', evaluation:null, selectedModels:new Set(), busy:false };
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const formatValue = (value) => value === null || value === undefined ? '—' : typeof value === 'number' ? value.toFixed(4) : escapeHtml(value);
const showMessage = (target, text, type='error') => { const el = typeof target === 'string' ? $(target) : target; el.textContent = text; el.className = `message ${type}`; };
const hideMessage = (target) => { const el = typeof target === 'string' ? $(target) : target; el.classList.add('hidden'); };
const setBusy = (button, busy, label) => { button.disabled = busy; button.dataset.label ||= button.innerHTML; button.innerHTML = busy ? `⏳ ${label}` : button.dataset.label; };

async function request(path, options={}) {
  const response = await fetch(`${API.base()}${path}`, { headers:{'Content-Type':'application/json', ...(options.headers||{})}, ...options });
  let payload; try { payload = await response.json(); } catch { payload = {}; }
  if (!response.ok) throw new Error(payload.detail || payload.message || `Backend trả về lỗi HTTP ${response.status}.`);
  return payload;
}

function init() {
  $('#builderName').innerHTML = BUILDERS.map(([key,label]) => `<option value="${key}">${label}</option>`).join('');
  $('#splitStrategy').innerHTML = Object.entries(SPLITS).map(([key, item]) => `<option value="${key}">${item.label}</option>`).join('');
  $('#metrics').innerHTML = METRICS.map(([key,label], i) => `<label class="check-item"><input type="checkbox" value="${key}" ${i < 3 ? 'checked' : ''}/> ${label}</label>`).join('');
  $('#algorithms').innerHTML = ALGORITHMS.map(algorithmCard).join('');
  renderSplitParameters();
  bindEvents();
  loadDatasets();
  updateConnection('Đang kiểm tra…', 'muted');
}

function algorithmCard(item) {
  const fields = item.fields.map(([key,label,type,choices]) => type === 'select' ? `<label>${label}<select data-field="${key}">${choices.map(v => `<option value="${v}">${v}</option>`).join('')}</select></label>` : `<label>${label}<input data-field="${key}" type="${type}" step="any" placeholder="Mặc định" /></label>`).join('');
  return `<article class="algorithm-card" data-algorithm="${item.key}"><div class="algorithm-card-head"><input class="algorithm-toggle" type="checkbox" value="${item.key}" /><div><strong>${item.name}</strong><p>${item.description}</p></div></div><div class="algorithm-fields hidden">${fields}</div></article>`;
}

async function loadDatasets() {
  const select = $('#existingDataset');
  select.innerHTML = '<option value="">Đang tải danh sách...</option>';
  try {
    const payload = await request('/datasets/');
    const datasets = Array.isArray(payload.datasets) ? payload.datasets : [];
    select.innerHTML = datasets.length
      ? '<option value="">Chọn Dataset</option>' + datasets.map((item) => {
        const name = typeof item === 'string' ? item : item.dataset_name;
        const size = typeof item === 'object' && item.file_size ? ` · ${Math.ceil(item.file_size / 1024)} KB` : '';
        return `<option value="${escapeHtml(name)}">${escapeHtml(name)}${size}</option>`;
      }).join('')
      : '<option value="">Chưa có Dataset</option>';
    updateConnection('Backend đã kết nối', 'good');
  } catch (error) {
    select.innerHTML = '<option value="">Không tải được Dataset</option>';
    updateConnection('Không kết nối được Backend', 'bad');
    showMessage('#globalMessage', error.message);
  }
}

function updateConnection(text, status) { $('#connectionText').textContent = text; $('#connectionDot').className = `dot dot-${status}`; }
function renderSplitParameters() { const config = SPLITS[$('#splitStrategy').value]; $('#splitParameters').innerHTML = config.fields.map(([key,label,type,value]) => `<label>${label}<input data-split-field="${key}" type="${type}" value="${value ?? ''}" ${key === 'test_size' && value === '' ? 'placeholder="Để trống để Backend tự tính"' : ''}/></label>`).join(''); }
function collectSplit() { const parameters = {}; $$('#splitParameters [data-split-field]').forEach(input => { if (input.value !== '') parameters[input.dataset.splitField] = input.type === 'number' ? Number(input.value) : input.value; }); return { strategy:$('#splitStrategy').value, parameters }; }
function collectAlgorithms() { const algorithms = {}; $$('.algorithm-card').filter(card => card.querySelector('.algorithm-toggle').checked).forEach(card => { const config = {}; card.querySelectorAll('[data-field]').forEach(input => { if (input.value !== '') config[input.dataset.field] = input.type === 'number' ? Number(input.value) : input.value; }); algorithms[card.dataset.algorithm] = config; }); return algorithms; }
function datasetPayload() { if (state.datasetMode === 'existing') { const dataset_name = $('#existingDataset').value; if (!dataset_name) throw new Error('Hãy chọn một Dataset có sẵn.'); return { source:'existing', dataset_name }; } const tickers = $('#tickers').value.split(',').map(x => x.trim()).filter(Boolean); const dataset_name = $('#newDatasetName').value.trim(); if (!dataset_name || !$('#builderName').value || !tickers.length || !$('#startDate').value || !$('#endDate').value) throw new Error('Hãy điền đầy đủ thông tin Dataset mới.'); return { source:'new', dataset_name, builder_name:$('#builderName').value, tickers, start_date:$('#startDate').value, end_date:$('#endDate').value }; }

async function evaluate() { const button = $('#evaluateButton'); try { const algorithms = collectAlgorithms(); const metrics = $$('#metrics input:checked').map(x => x.value); if (!Object.keys(algorithms).length) throw new Error('Hãy chọn ít nhất một thuật toán.'); if (!metrics.length) throw new Error('Hãy chọn ít nhất một Metric.'); const payload = { dataset:datasetPayload(), algorithms, metrics, split:collectSplit() }; setBusy(button,true,'Đang đánh giá…'); hideMessage('#globalMessage'); state.evaluation = await request('/local-ai/evaluations', {method:'POST', body:JSON.stringify(payload)}); state.selectedModels = new Set(); renderEvaluation(); goTo(2); } catch (error) { showMessage('#globalMessage', error.message); } finally { setBusy(button,false); } }

function renderEvaluation() { const result = state.evaluation; const dataset = result.dataset; const split = result.evaluation?.split || {}; $('#evaluationSummary').innerHTML = [['Dataset',dataset.dataset_name],['Nguồn',dataset.source === 'new' ? 'Dataset mới' : 'Dataset có sẵn'],['Chia dữ liệu',SPLITS[split.strategy]?.label || split.strategy],['Số dòng',dataset.row_count]].map(([label,value]) => `<div class="summary-item"><small>${label}</small><strong>${escapeHtml(value)}</strong></div>`).join(''); const statusClass = result.status === 'success' ? 'success' : result.status === 'partial_success' ? 'info' : 'error'; showMessage('#evaluationStatus', result.status === 'success' ? 'Đánh giá hoàn tất. Chọn các thuật toán muốn huấn luyện chính thức.' : result.status === 'partial_success' ? 'Một số thuật toán đã đánh giá thành công; hãy kiểm tra từng dòng trước khi chọn.' : 'Toàn bộ thuật toán đánh giá thất bại.', statusClass); const algorithms = result.evaluation?.algorithms || []; const metrics = result.evaluation?.metrics || []; $('#resultsTable').innerHTML = `<thead><tr><th>Giữ lại</th><th>Thuật toán</th><th>Trạng thái</th>${metrics.map(metric => `<th>${escapeHtml(metric)}</th>`).join('')}<th>Split thành công</th><th>Lỗi</th></tr></thead><tbody>${algorithms.map(item => `<tr><td><input class="select-model" type="checkbox" data-model="${escapeHtml(item.algorithm)}" ${item.status === 'failed' ? 'disabled' : ''}/></td><td><strong>${escapeHtml(algorithmName(item.algorithm))}</strong></td><td><span class="status-pill status-${item.status.replace('_','')}">${statusLabel(item.status)}</span></td>${metrics.map(metric => `<td>${formatValue(item.metrics?.[metric])}</td>`).join('')}<td>${item.split_count ?? 0}</td><td>${item.errors?.length ? `<span title="${escapeHtml(item.errors.map(e => e.error).join('\n'))}">${item.errors.length} lỗi</span>` : '—'}</td></tr>`).join('')}</tbody>`; $$('#resultsTable [data-model]').forEach(input => input.addEventListener('change', () => { input.checked ? state.selectedModels.add(input.dataset.model) : state.selectedModels.delete(input.dataset.model); $('#trainButton').disabled = !state.selectedModels.size; })); }

function algorithmName(key) { return ALGORITHMS.find(item => item.key === key)?.name || key; }
function statusLabel(status) { return ({success:'Thành công',partial_success:'Một phần',failed:'Thất bại'})[status] || status; }
function statusClassName(status) { return status === 'partial_success' ? 'partial' : status; }
function trainingPayload() { const configs = Object.fromEntries([...state.selectedModels].map(key => { const card = $(`[data-algorithm="${key}"]`); const config = {}; card?.querySelectorAll('[data-field]').forEach(input => { if (input.value !== '') config[input.dataset.field] = input.type === 'number' ? Number(input.value) : input.value; }); return [key, config]; })); return { dataset_name:state.evaluation.dataset.dataset_name, algorithms:configs }; }

async function train() { const button = $('#trainButton'); try { setBusy(button,true,'Đang chuẩn bị…'); const payload = trainingPayload(); $('#trainingSummary').innerHTML = `<strong>Dataset:</strong> ${escapeHtml(payload.dataset_name)} &nbsp;·&nbsp; <strong>Thuật toán:</strong> ${[...state.selectedModels].map(algorithmName).map(escapeHtml).join(', ')}`; showMessage('#trainingStatus','Backend đang huấn luyện model mới trên toàn bộ Dataset…','info'); goTo(3); state.training = await request('/local-ai/train',{method:'POST',body:JSON.stringify(payload)}); renderTraining(); } catch(error) { showMessage('#trainingStatus',error.message); } finally { setBusy(button,false); } }
function renderTraining() { const result = state.training; const type = result.status === 'success' ? 'success' : result.status === 'partial_success' ? 'info' : 'error'; showMessage('#trainingStatus', result.status === 'success' ? 'Huấn luyện hoàn tất và model đã được lưu.' : result.status === 'partial_success' ? 'Một số model đã lưu thành công, một số model thất bại.' : 'Huấn luyện thất bại cho tất cả thuật toán.', type); $('#trainingResults').innerHTML = (result.models || []).map(model => `<div class="model-result"><div><strong>${escapeHtml(algorithmName(model.algorithm))}</strong><small>${model.status === 'success' ? `Model ID: ${escapeHtml(model.model_id || '—')} · File: ${escapeHtml(model.file_name || '—')}` : `Lỗi: ${escapeHtml(model.error || 'Không rõ lỗi')}`}</small></div><span class="status-pill status-${model.status}">${model.status === 'success' ? 'Đã lưu' : 'Thất bại'}</span></div>`).join(''); }

function goTo(step) { $$('.step-panel').forEach(panel => panel.classList.toggle('hidden', panel.id !== `step${step}`)); $$('.step').forEach(item => item.classList.toggle('active', Number(item.dataset.step) === step)); window.scrollTo({top:0,behavior:'smooth'}); }
function bindEvents() { $$('.choice').forEach(button => button.addEventListener('click', () => { state.datasetMode = button.dataset.datasetMode; $$('.choice').forEach(x => x.classList.toggle('active', x === button)); $('#existingDatasetPanel').classList.toggle('hidden', state.datasetMode !== 'existing'); $('#newDatasetPanel').classList.toggle('hidden', state.datasetMode !== 'new'); })); $('#reloadDatasets').addEventListener('click',loadDatasets); $('#splitStrategy').addEventListener('change',renderSplitParameters); $$('.algorithm-card').forEach(card => card.querySelector('.algorithm-toggle').addEventListener('change', event => { card.classList.toggle('selected',event.target.checked); card.querySelector('.algorithm-fields').classList.toggle('hidden',!event.target.checked); })); $('#evaluateButton').addEventListener('click',evaluate); $('#backToConfig').addEventListener('click',()=>goTo(1)); $('#backToResults').addEventListener('click',()=>goTo(2)); $('#trainButton').addEventListener('click',train); $('#restartButton').addEventListener('click',()=>{ state.evaluation=null; state.training=null; state.selectedModels.clear(); goTo(1); }); $$('.step').forEach(button => button.addEventListener('click',()=>{ const target=Number(button.dataset.step); if(target===1 || (target===2 && state.evaluation) || (target===3 && state.training)) goTo(target); })); }
document.addEventListener('DOMContentLoaded',init);
