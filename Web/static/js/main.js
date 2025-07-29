// main.js for dashboard.html

document.addEventListener('DOMContentLoaded', () => {
    // 第一张图表的变量
    const offenceCatSelect = document.getElementById('offence-category-select');
    const offenceSubcatSelect = document.getElementById('offence-subcategory-select');
    const punishmentCatSelect = document.getElementById('punishment-category-select');
    const punishmentSubcatSelect = document.getElementById('punishment-subcategory-select');
    const actToggle = document.getElementById('act-toggle');
    const actDesc = document.getElementById('act-desc');
    const actDetails = document.getElementById('act-details');
    const campaignToggle = document.getElementById('campaign-toggle');
    const campaignActsList = document.getElementById('campaign-acts-list');
    const campaignDetails = document.getElementById('campaign-details');
    let actInfo = null;
    let campaignActs = [];
    let allOptions = {};
    const transportationToggle = document.getElementById('transportation-toggle');
    const transportationActsList = document.getElementById('transportation-acts-list');
    const transportationDetails = document.getElementById('transportation-details');
    let transportationActs = [];

    // 第二张图表的变量
    const barGroupbySelect = document.getElementById('bar-groupby-select');
    const barYearStartSelect = document.getElementById('bar-year-start-select');
    const barYearEndSelect = document.getElementById('bar-year-end-select');
    const barExcludeDeathCheckbox = document.getElementById('bar-exclude-death');

    // 第三张图表的变量
    const imprisonAnalysisSelect = document.getElementById('imprison-analysis-select');
    const imprisonYearStartSelect = document.getElementById('imprison-year-start-select');
    const imprisonYearEndSelect = document.getElementById('imprison-year-end-select');

    // 加载所有选项
    fetch('/api/options')
        .then(res => res.json())
        .then(data => {
            allOptions = data;
            fillSelect(offenceCatSelect, data.offence_categories);
            fillSelect(offenceSubcatSelect, data.offence_subcategories);
            fillSelect(punishmentCatSelect, data.punishment_categories);
            fillSelect(punishmentSubcatSelect, data.punishment_subcategories);
            updateChart();
        });

    // 加载act信息
    fetch('/api/acts')
        .then(res => res.json())
        .then(data => {
            actInfo = data;
            renderActActs();
        });

    // 加载campaign信息
    fetch('/api/campaigns')
        .then(res => res.json())
        .then(data => {
            campaignActs = data.acts;
            renderCampaignActs();
        });

    // 加载transportation信息
    fetch('/api/transportation')
        .then(res => res.json())
        .then(data => {
            transportationActs = data.acts;
            renderTransportationActs();
        });

    // 绑定第一张图表的筛选器（卡片内部）
    offenceCatSelect.addEventListener('change', () => {
        updateSubcategorySelect(offenceCatSelect, offenceSubcatSelect, allOptions.offence_subcategories_map);
        updateChart();
    });
    offenceSubcatSelect.addEventListener('change', updateChart);
    punishmentCatSelect.addEventListener('change', () => {
        updateSubcategorySelect(punishmentCatSelect, punishmentSubcatSelect, allOptions.punishment_subcategories_map);
        updateChart();
    });
    punishmentSubcatSelect.addEventListener('change', updateChart);

    actToggle.addEventListener('change', () => {
        updateChart();
    });
    campaignToggle.addEventListener('change', () => {
        updateChart();
    });
    transportationToggle.addEventListener('change', () => {
        updateChart();
    });

    // 加载年份数据，然后初始化第二张和第三张图表
    fetch('/api/line_data')
        .then(res => res.json())
        .then(data => {
            const years = data.years;
            
            // 初始化第二张图表
    
            fillYearSelect(barYearStartSelect, years);
            fillYearSelect(barYearEndSelect, years);
            barYearStartSelect.value = years[0];
            barYearEndSelect.value = years[years.length - 1];
            
            // 确保group by有默认值
            if (!barGroupbySelect.value) {
                barGroupbySelect.value = 'offence_category';
            }
            
            // 初始化第三张图表
            fillYearSelect(imprisonYearStartSelect, years);
            fillYearSelect(imprisonYearEndSelect, years);
            imprisonYearStartSelect.value = years[0];
            imprisonYearEndSelect.value = years[years.length - 1];
            
            // 加载初始图表
            updateBarChart();
            updateImprisonChart();
        });

    // 绑定第二张图表的事件监听器
    barGroupbySelect.addEventListener('change', updateBarChart);
    barYearStartSelect.addEventListener('change', updateBarChart);
    barYearEndSelect.addEventListener('change', updateBarChart);
    barExcludeDeathCheckbox.addEventListener('change', updateBarChart);

    // 绑定第三张图表的事件监听器
    imprisonAnalysisSelect.addEventListener('change', updateImprisonChart);
    imprisonYearStartSelect.addEventListener('change', updateImprisonChart);
    imprisonYearEndSelect.addEventListener('change', updateImprisonChart);

    function renderActActs() {
        const actActsList = document.getElementById('act-acts-list');
        if (actInfo) {
            actActsList.innerHTML = '';
            const li = document.createElement('li');
            li.innerHTML = `<span class="act-title">${actInfo.year} - ${actInfo.title}</span><div class="act-desc">${actInfo.description}</div>`;
            li.querySelector('.act-title').addEventListener('click', () => {
                li.classList.toggle('expanded');
            });
            actActsList.appendChild(li);
        }
    }

    function renderCampaignActs() {
        campaignActsList.innerHTML = '';
        campaignActs.forEach((act, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="act-title">${act.year} - ${act.title}</span><div class="act-desc">${act.description}</div>`;
            li.querySelector('.act-title').addEventListener('click', () => {
                li.classList.toggle('expanded');
            });
            campaignActsList.appendChild(li);
        });
    }

    function renderTransportationActs() {
        transportationActsList.innerHTML = '';
        transportationActs.forEach((act, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="act-title">${act.year} - ${act.title}</span><div class="act-desc">${act.description}</div>`;
            li.querySelector('.act-title').addEventListener('click', () => {
                li.classList.toggle('expanded');
            });
            transportationActsList.appendChild(li);
        });
    }

    function fillSelect(select, options) {
        select.innerHTML = '<option value="">All</option>';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }

    function fillYearSelect(select, options) {
        select.innerHTML = '';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }

    function updateSubcategorySelect(catSelect, subcatSelect, map) {
        const selectedCategory = catSelect.value;
        if (selectedCategory && map[selectedCategory]) {
            fillSelect(subcatSelect, map[selectedCategory]);
        } else {
            fillSelect(subcatSelect, []);
        }
    }

    function updateChart() {
        const offence = offenceCatSelect.value;
        const offenceSub = offenceSubcatSelect.value;
        const punishment = punishmentCatSelect.value;
        const punishmentSub = punishmentSubcatSelect.value;
        
        const params = new URLSearchParams();
        if (offence) params.append('offence_category', offence);
        if (offenceSub) params.append('offence_subcategory', offenceSub);
        if (punishment) params.append('punishment_category', punishment);
        if (punishmentSub) params.append('punishment_subcategory', punishmentSub);
        
        fetch(`/api/line_data?${params}`)
            .then(res => res.json())
            .then(data => {
                drawLineChart(data);
            });
    }

    function drawLineChart(data) {
        d3.select('#chart').selectAll('*').remove();
        
        if (!data.years || data.years.length === 0) {
            d3.select('#chart')
                .append('div')
                .style('text-align', 'center')
                .style('color', '#666')
                .style('font-size', '16px')
                .text('No data available for selected criteria');
            return;
        }

        const margin = {top: 60, right: 40, bottom: 60, left: 80};
        const width = 800 - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;
        const svg = d3.select('#chart')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // x轴（年份）
        const x = d3.scaleLinear()
            .domain(d3.extent(data.years))
            .range([0, width]);
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).tickFormat(d3.format('d')));

        // y轴（比例）
        const y = d3.scaleLinear()
            .domain([0, d3.max(data.rates)])
            .nice()
            .range([height, 0]);
        svg.append('g')
            .call(d3.axisLeft(y).tickFormat(d => (d * 100).toFixed(1) + '%'));

        // 折线
        const line = d3.line()
            .x((d, i) => x(data.years[i]))
            .y((d, i) => y(data.rates[i]));

        svg.append('path')
            .datum(data.rates)
            .attr('fill', 'none')
            .attr('stroke', '#0074D9')
            .attr('stroke-width', 3)
            .attr('d', line);

        // 数据点
        svg.selectAll('circle')
            .data(data.years)
            .enter()
            .append('circle')
            .attr('cx', (d, i) => x(data.years[i]))
            .attr('cy', (d, i) => y(data.rates[i]))
            .attr('r', 4)
            .attr('fill', '#0074D9')
            .on('mouseover', function(e, d) {
                const i = data.years.indexOf(d);
                showTooltip(e, d, data.rates[i], data.counts[i]);
            })
            .on('mouseout', hideTooltip);

        // Campaign Acts shaded period
        if (campaignToggle.checked && campaignActs.length > 0) {
            const yearsArr = campaignActs.map(act => act.year).filter(y => y >= d3.min(data.years) && y <= d3.max(data.years));
            if (yearsArr.length > 0) {
                const minYear = Math.min(...yearsArr);
                const maxYear = Math.max(...yearsArr);
                svg.append('rect')
                    .attr('x', x(minYear))
                    .attr('y', 0)
                    .attr('width', x(maxYear) - x(minYear))
                    .attr('height', height)
                    .attr('fill', '#888')
                    .attr('opacity', 0.13);
            }
        }

        // Prison Act 1835 marker
        if (actToggle.checked && actInfo) {
            const actYear = actInfo.year;
            if (actYear >= d3.min(data.years) && actYear <= d3.max(data.years)) {
                svg.append('line')
                    .attr('x1', x(actYear))
                    .attr('x2', x(actYear))
                    .attr('y1', 0)
                    .attr('y2', height)
                    .attr('stroke', '#FF4136')
                    .attr('stroke-width', 2)
                    .attr('stroke-dasharray', '6,4');
                
                // 智能文字位置：避免超出边界
                const textX = x(actYear);
                const textOffset = textX > width - 100 ? -8 : 8; // 如果接近右边界，文字放在线的左边
                const rotation = textX > width - 100 ? `rotate(90,${textX + textOffset},40)` : `rotate(-90,${textX + textOffset},40)`;
                
                svg.append('text')
                    .attr('x', textX + textOffset)
                    .attr('y', 40)
                    .attr('fill', '#FF4136')
                    .attr('transform', rotation)
                    .style('font-size', '11px')
                    .style('text-anchor', 'start')
                    .text(actInfo.title);
            }
        }

        // Campaign Acts markers
        if (campaignToggle.checked && campaignActs.length > 0) {
            campaignActs.forEach((act, idx) => {
                if (act.year >= d3.min(data.years) && act.year <= d3.max(data.years)) {
                    svg.append('line')
                        .attr('x1', x(act.year))
                        .attr('x2', x(act.year))
                        .attr('y1', 0)
                        .attr('y2', height)
                        .attr('stroke', '#0074D9')
                        .attr('stroke-width', 2)
                        .attr('stroke-dasharray', '4,4');
                    
                    // 智能文字位置：避免超出边界和重叠
                    const textX = x(act.year);
                    const textOffset = textX > width - 120 ? -8 : 8;
                    const yPosition = 60 + (idx % 3) * 20; // 错开Y位置避免重叠
                    const rotation = textX > width - 120 ? `rotate(90,${textX + textOffset},${yPosition})` : `rotate(-90,${textX + textOffset},${yPosition})`;
                    
                    svg.append('text')
                        .attr('x', textX + textOffset)
                        .attr('y', yPosition)
                        .attr('fill', '#0074D9')
                        .attr('transform', rotation)
                        .style('font-size', '11px')
                        .style('text-anchor', 'start')
                        .text(act.title.length > 15 ? act.title.substring(0, 15) + '...' : act.title);
                }
            });
        }

        // Transportation Acts markers
        if (transportationToggle.checked && transportationActs.length > 0) {
            transportationActs.forEach((act, idx) => {
                if (act.year >= d3.min(data.years) && act.year <= d3.max(data.years)) {
                    svg.append('line')
                        .attr('x1', x(act.year))
                        .attr('x2', x(act.year))
                        .attr('y1', 0)
                        .attr('y2', height)
                        .attr('stroke', '#2ECC40')
                        .attr('stroke-width', 2)
                        .attr('stroke-dasharray', '5,5');
                    
                    // 智能文字位置：避免超出边界
                    const textX = x(act.year);
                    const textOffset = textX > width - 100 ? -8 : 8;
                    const yPosition = 100 + (idx % 2) * 20; // Transportation acts在更下方，避免与campaign重叠
                    const rotation = textX > width - 100 ? `rotate(90,${textX + textOffset},${yPosition})` : `rotate(-90,${textX + textOffset},${yPosition})`;
                    
                    svg.append('text')
                        .attr('x', textX + textOffset)
                        .attr('y', yPosition)
                        .attr('fill', '#2ECC40')
                        .attr('transform', rotation)
                        .style('font-size', '11px')
                        .style('text-anchor', 'start')
                        .text(act.title.length > 15 ? act.title.substring(0, 15) + '...' : act.title);
                }
            });
        }
    }

    function updateBarChart() {
        const groupBy = barGroupbySelect.value;
        const startYear = barYearStartSelect.value;
        const endYear = barYearEndSelect.value;
        const excludeDeath = barExcludeDeathCheckbox.checked ? 1 : 0;
        
        fetch(`/api/bar_data?group_by=${groupBy}&start_year=${startYear}&end_year=${endYear}&exclude_death=${excludeDeath}`)
            .then(res => res.json())
            .then(data => {
                drawBarChart(data);
            });
    }

    function drawBarChart(data) {
        d3.select('#bar-chart').selectAll('*').remove();
        
        if (!data.groups || data.groups.length === 0) {
            d3.select('#bar-chart')
                .append('div')
                .style('text-align', 'center')
                .style('color', '#666')
                .style('font-size', '16px')
                .text('No data available for selected criteria');
          return;
        }

        // 创建一个容器来实现水平布局（图表+图例）
        const container = d3.select('#bar-chart')
            .append('div')
            .style('display', 'flex')
            .style('justify-content', 'center')
            .style('align-items', 'flex-start')
            .style('gap', '30px');
            
        const chartContainer = container.append('div');
        
        const margin = {top: 40, right: 40, bottom: 80, left: 120};
        const width = 600 - margin.left - margin.right; // 减小宽度为图例留空间
        const height = Math.max(400, data.groups.length * 50) - margin.top - margin.bottom;
        
        const svg = chartContainer
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // y轴（组别）
        const y = d3.scaleBand()
            .domain(data.groups)
            .range([0, height])
            .padding(0.1);
        svg.append('g')
            .call(d3.axisLeft(y));

        // x轴（比例）
        const x = d3.scaleLinear()
            .domain([0, 1])
            .range([0, width]);
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).tickFormat(d3.format('.0%')));

        // 堆叠数据
        const stack = d3.stack()
            .keys(data.punishment_categories)
            .value((d, key) => d[key] || 0);

        const transformedData = data.groups.map(group => {
            const row = {group: group};
            data.punishment_categories.forEach(cat => {
                row[cat] = (data.data && data.data[group] && data.data[group][cat]) || 0;
            });
            return row;
        });
        
        const stackedData = stack(transformedData);

        // 颜色比例尺
        const color = d3.scaleOrdinal()
            .domain(data.punishment_categories)
            .range(d3.schemeSet2);

        // 绘制堆叠条形图
        const groups = svg.selectAll('.group')
            .data(stackedData)
            .enter()
            .append('g')
            .attr('class', 'group');
            
        groups.selectAll('rect')
            .data(d => d)
            .enter()
            .append('rect')
            .attr('x', d => x(d[0]))
            .attr('y', d => y(d.data.group))
            .attr('width', d => x(d[1]) - x(d[0]))
            .attr('height', y.bandwidth())
            .attr('fill', (d, i, nodes) => {
                // 获取父级组的key（punishment类型）
                const parentData = d3.select(nodes[i].parentNode).datum();
                return color(parentData.key);
            })
            .on('mouseover', function(e, d) {
                const rate = (d[1] - d[0]) * 100;
                // 获取父级组的key（punishment类型）
                const parentData = d3.select(this.parentNode).datum();
                showBarTooltip(e, d.data.group, parentData.key, rate);
            })
            .on('mouseout', hideBarTooltip);

        // 垂直图例
        const legend = container.append('div')
            .style('display', 'flex')
            .style('flex-direction', 'column')
            .style('margin-top', '40px');
            
        // 图例标题
        legend.append('div')
            .style('font-weight', 'bold')
            .style('margin-bottom', '10px')
            .style('font-size', '14px')
            .text('Punishment Types');

        data.punishment_categories.forEach(category => {
            const legendItem = legend.append('div')
                .style('display', 'flex')
                .style('align-items', 'center')
                .style('margin-bottom', '8px')
                .style('font-size', '12px');
            
            legendItem.append('div')
                .style('width', '16px')
                .style('height', '16px')
                .style('background-color', color(category))
                .style('margin-right', '8px')
                .style('border', '1px solid #ccc');
            
            legendItem.append('span')
                .text(category)
                .style('text-transform', 'capitalize');
        });
    }

    function updateImprisonChart() {
        const start = imprisonYearStartSelect.value;
        const end = imprisonYearEndSelect.value;
        const analysis = imprisonAnalysisSelect.value;
        if (parseInt(start) > parseInt(end)) return;
        fetch(`/api/imprison_data?start_year=${start}&end_year=${end}&analysis_type=${analysis}`)
            .then(res => res.json())
            .then(data => {
                drawImprisonChart(data);
            });
    }

    function drawImprisonChart(data) {
        d3.select('#imprison-chart').selectAll('*').remove();
        
        if ((data.type === 'avg_sentence' || data.type === 'theft_value' || data.type === 'habitual_vs_first' || data.type === 'violent_crime') && data.categories.length > 0) {
            const margin = {top: 40, right: 40, bottom: 80, left: 80};
            const width = 800 - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;
            const svg = d3.select('#imprison-chart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
                .append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // x轴（类别）
            const x = d3.scaleBand()
                .domain(data.categories)
                .range([0, width])
                .padding(0.2);
            svg.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x))
                .selectAll('text')
                .attr('transform', 'rotate(-30)')
                .style('text-anchor', 'end');
            
            // y轴（平均刑期）
            const y = d3.scaleLinear()
                .domain([0, d3.max(data.values)])
                .nice()
                .range([height, 0]);
            svg.append('g')
                .call(d3.axisLeft(y).tickFormat(d => d.toFixed(1) + ' yrs'));
            
            // 颜色方案
            const colorSchemes = {
                'avg_sentence': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'],
                'theft_value': ['#FF8C42', '#FF6B9D', '#4ECDC4', '#45B7D1'],
                'violent_crime': ['#E74C3C', '#C0392B', '#E67E22', '#D35400'],
                'habitual_vs_first': ['#3498DB', '#2980B9']
            };

            const colors = colorSchemes[data.type] || ['#0074D9'];

            // 绘制条形图
            svg.selectAll('rect')
                .data(data.categories)
                .enter()
                .append('rect')
                .attr('x', d => x(d))
                .attr('y', (d, i) => y(data.values[i]))
                .attr('width', x.bandwidth())
                .attr('height', (d, i) => height - y(data.values[i]))
                .attr('fill', (d, i) => colors[i % colors.length])
                .attr('stroke', '#fff')
                .attr('stroke-width', 1)
                .on('mouseover', function(e, d) {
                    const i = data.categories.indexOf(d);
                    d3.select(this)
                        .attr('opacity', 0.8)
                        .attr('stroke-width', 2);
                    showImprisonTooltip(e, d, data.values[i], data.counts[i], data.type);
                })
                .on('mouseout', function() {
                    d3.select(this)
                        .attr('opacity', 1)
                        .attr('stroke-width', 1);
                    hideImprisonTooltip();
                });
            
            // 标题
            let title = '';
            if (data.type === 'avg_sentence') {
                title = 'Average Sentence by Offence Category';
            } else if (data.type === 'theft_value') {
                title = 'Average Sentence by Theft Value';
            } else if (data.type === 'habitual_vs_first') {
                title = 'Average Sentence: Habitual vs First-time Offenders';
            } else if (data.type === 'violent_crime') {
                title = 'Average Sentence by Violent Crime Type';
            }
            
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', -10)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .style('font-weight', 'bold')
                .text(title);
        } else {
            // 显示占位信息
            d3.select('#imprison-chart')
                .append('div')
                .style('text-align', 'center')
                .style('color', '#666')
                .style('font-size', '16px')
                .text(data.message || 'No data available for selected criteria');
        }
    }

    // Tooltip 函数
    let imprisonTooltip = d3.select('#imprison-chart-tooltip');
    if (imprisonTooltip.empty()) {
        imprisonTooltip = d3.select('body').append('div')
            .attr('id', 'imprison-chart-tooltip')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('background', '#fff')
            .style('border', '1px solid #ccc')
            .style('padding', '8px 12px')
            .style('border-radius', '4px')
            .style('pointer-events', 'none')
            .style('display', 'none');
    }

    function showImprisonTooltip(event, category, avgSentence, count, analysisType) {
        let label = 'Offence';
        if (analysisType === 'theft_value') {
            label = 'Theft Value';
        } else if (analysisType === 'habitual_vs_first') {
            label = 'Offender Type';
        } else if (analysisType === 'violent_crime') {
            label = 'Violent Crime Type';
        }
        
        imprisonTooltip.style('display', 'block')
            .html(`<b>${label}:</b> ${category}<br><b>Avg Sentence:</b> ${avgSentence.toFixed(2)} years<br><b>Case Count:</b> ${count}`)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    function hideImprisonTooltip() {
        imprisonTooltip.style('display', 'none');
    }

    // 其他 Tooltip 函数
    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('position', 'absolute')
        .style('background', '#fff')
        .style('border', '1px solid #ccc')
        .style('padding', '8px 12px')
        .style('border-radius', '4px')
        .style('pointer-events', 'none')
        .style('display', 'none');

    function showTooltip(event, year, rate, count) {
        tooltip.style('display', 'block')
            .html(`<b>Year:</b> ${year}<br><b>Rate:</b> ${(rate*100).toFixed(2)}%<br><b>Count:</b> ${count}`)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    function hideTooltip() {
        tooltip.style('display', 'none');
    }

    let barTooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('position', 'absolute')
        .style('background', '#fff')
        .style('border', '1px solid #ccc')
        .style('padding', '8px 12px')
        .style('border-radius', '4px')
        .style('pointer-events', 'none')
        .style('display', 'none');

    function showBarTooltip(event, group, punishment, rate) {
        barTooltip.style('display', 'block')
            .html(`<b>Group:</b> ${group}<br><b>Punishment:</b> ${punishment}<br><b>Rate:</b> ${rate.toFixed(2)}%`)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    function hideBarTooltip() {
        barTooltip.style('display', 'none');
    }
});
