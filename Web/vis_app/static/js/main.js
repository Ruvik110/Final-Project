document.addEventListener('DOMContentLoaded', () => {
    // Helper function to get x-axis label based on analysis type
    function getXAxisLabel(analysisType) {
        switch(analysisType) {
            case 'avg_sentence':
                return 'Offence Category';
            case 'theft_value':
                return 'Theft Value Category';
            case 'habitual_vs_first':
                return 'Offender Type';
            case 'violent_crime':
                return 'Violent Crime Type';
            default:
                return 'Category';
        }
    }

    // variables for the first
    const offenceCatSelect = document.getElementById('offence-category-select');
    const offenceSubcatSelect = document.getElementById('offence-subcategory-select');
    const punishmentCatSelect = document.getElementById('punishment-category-select');
    const punishmentSubcatSelect = document.getElementById('punishment-subcategory-select');
    const actToggle = document.getElementById('act-toggle');
    const campaignToggle = document.getElementById('campaign-toggle');
    const campaignActsList = document.getElementById('campaign-acts-list');
    let actInfo = null;
    let campaignActs = [];
    let allOptions = {};
    const transportationToggle = document.getElementById('transportation-toggle');
    const transportationActsList = document.getElementById('transportation-acts-list');
    let transportationActs = [];

    // variables for the second
    const barGroupbySelect = document.getElementById('bar-groupby-select');
    const barYearStartSelect = document.getElementById('bar-year-start-select');
    const barYearEndSelect = document.getElementById('bar-year-end-select');
    const barExcludeDeathCheckbox = document.getElementById('bar-exclude-death');

    // variables for the third
    const imprisonAnalysisSelect = document.getElementById('imprison-analysis-select');
    const imprisonYearStartSelect = document.getElementById('imprison-year-start-select');
    const imprisonYearEndSelect = document.getElementById('imprison-year-end-select');
    const imprisonShowAverageCheckbox = document.getElementById('imprison-show-average');

    // load all options
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

    // act info
    fetch('/api/acts')
        .then(res => res.json())
        .then(data => {
            actInfo = data;
            renderActActs();
        });

    // campaign info
    fetch('/api/campaigns')
        .then(res => res.json())
        .then(data => {
            campaignActs = data.acts;
            renderCampaignActs();
        });

    // transportation info
    fetch('/api/transportation')
        .then(res => res.json())
        .then(data => {
            transportationActs = data.acts;
            renderTransportationActs();
        });

    // bind the filters for the first
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

    // listen to the details element
    const detailsElements = document.querySelectorAll('details');
    detailsElements.forEach(details => {
        // initialize
        const panel = details.closest('.campaign-panel');
        if (panel && !details.open) {
            panel.classList.add('collapsed');
        }
        
        details.addEventListener('toggle', function() {
            const panel = this.closest('.campaign-panel');
            if (panel) {
                if (this.open) {
                    panel.classList.remove('collapsed');
                } else {
                    panel.classList.add('collapsed');
                }
            }
        });
    });

    // load years then initialize the second and third charts
    fetch('/api/line_data')
        .then(res => res.json())
        .then(data => {
            const years = data.years;
    
            fillYearSelect(barYearStartSelect, years);
            fillYearSelect(barYearEndSelect, years);
            barYearStartSelect.value = years[0];
            barYearEndSelect.value = years[years.length - 1];
            
            // ensure group by has default
            if (!barGroupbySelect.value) {
                barGroupbySelect.value = 'offence_category';
            }
            
            fillYearSelect(imprisonYearStartSelect, years);
            fillYearSelect(imprisonYearEndSelect, years);
            imprisonYearStartSelect.value = years[0];
            imprisonYearEndSelect.value = years[years.length - 1];
            
            // the dropdown options
            if (barGroupbySelect) {
                const hisclassOption = barGroupbySelect.querySelector('option[value="hisclass"]');
                if (hisclassOption) {
                    hisclassOption.textContent = 'Social Class';
                }
            }
            
            // initialize the checkbox
            if (barGroupbySelect && barGroupbySelect.value === 'hisclass') {
                insertHisclassDetailCheckbox();
            }
            
            // load the initial charts
            updateBarChart();
            updateImprisonChart();
        });

    // checkbox functions
    let hisclassDetailCheckbox = null;
    function insertHisclassDetailCheckbox() {
        // clean up the old checkbox
        const existingLabel = document.getElementById('hisclass-detail-label');
        if (existingLabel) {
            existingLabel.remove();
        }
        
        if (!document.getElementById('hisclass-detail-checkbox')) {
            const barFilters = document.querySelector('.bar-filters');
            if (barFilters) {
                const label = document.createElement('label');
                label.id = 'hisclass-detail-label';
                label.style.fontSize = '1.08em';
                label.style.color = '#333';
                label.style.display = 'flex';
                label.style.alignItems = 'center';
                label.style.gap = '8px';
                label.style.minWidth = '180px';
                label.innerHTML = '<input type="checkbox" id="hisclass-detail-checkbox"> Show 1-12 Social Classes';
                barFilters.appendChild(label);
                hisclassDetailCheckbox = document.getElementById('hisclass-detail-checkbox');
                hisclassDetailCheckbox.addEventListener('change', updateBarChart);
            }
        } else {
            hisclassDetailCheckbox = document.getElementById('hisclass-detail-checkbox');
        }
    }
    
    function removeHisclassDetailCheckbox() {
        const existingLabel = document.getElementById('hisclass-detail-label');
        if (existingLabel) {
            existingLabel.remove();
        }
    }

    // bind the second 
    
    // listen to the group by change
    barGroupbySelect.addEventListener('change', () => {
        if (barGroupbySelect.value === 'hisclass') {
            insertHisclassDetailCheckbox();
        } else {
            removeHisclassDetailCheckbox();
        }
        updateBarChart();
    });
    
    // other listeners
    barYearStartSelect.addEventListener('change', updateBarChart);
    barYearEndSelect.addEventListener('change', updateBarChart);
    barExcludeDeathCheckbox.addEventListener('change', updateBarChart);

    // bind the third
    imprisonAnalysisSelect.addEventListener('change', () => {
        // uncheck the checkbox
        if (imprisonAnalysisSelect.value === 'theft_value' || imprisonAnalysisSelect.value === 'habitual_vs_first') {
            imprisonShowAverageCheckbox.checked = false;
        }
        updateImprisonChart();
    });
    imprisonYearStartSelect.addEventListener('change', updateImprisonChart);
    imprisonYearEndSelect.addEventListener('change', updateImprisonChart);
    imprisonShowAverageCheckbox.addEventListener('change', updateImprisonChart);

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

    function renderActsList(container, acts) {
        container.innerHTML = '';
        acts.forEach((act, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="act-title">${act.year} - ${act.title}</span><div class="act-desc">${act.description}</div>`;
            li.querySelector('.act-title').addEventListener('click', () => {
                li.classList.toggle('expanded');
            });
            container.appendChild(li);
        });
    }

    const renderCampaignActs = () => renderActsList(campaignActsList, campaignActs);
    const renderTransportationActs = () => renderActsList(transportationActsList, transportationActs);

    function fillSelect(select, options, hasAllOption = true) {
        select.innerHTML = hasAllOption ? '<option value="">All</option>' : '';
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }

    const fillYearSelect = (select, options) => fillSelect(select, options, false);

    function updateSubcategorySelect(catSelect, subcatSelect, map) {
        const selectedCategory = catSelect.value;
        if (selectedCategory && map[selectedCategory]) {
            fillSelect(subcatSelect, map[selectedCategory]);
        } else {
            // show all subcategories
            const allSubcategories = new Set();
            Object.values(map).forEach(subcats => {
                subcats.forEach(subcat => allSubcategories.add(subcat));
            });
            fillSelect(subcatSelect, Array.from(allSubcategories).sort());
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
            .style('display', 'block')
            .style('margin', '0 auto')
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // x axis
        const x = d3.scaleLinear()
            .domain(d3.extent(data.years))
            .range([0, width]);
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).tickFormat(d3.format('d')));

        // y axis
        const y = d3.scaleLinear()
            .domain([0, d3.max(data.rates)])
            .nice()
            .range([height, 0]);
        svg.append('g')
            .call(d3.axisLeft(y).tickFormat(d => (d * 100).toFixed(1) + '%'));

        // x axis label
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height + margin.bottom - 25)
            .attr('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('font-weight', 'bold')
            .text('Year');

        // y axis label
        svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -height / 2)
            .attr('y', -margin.left + 20)
            .attr('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('font-weight', 'bold')
            .text('Rate (%)');

        // line
        const line = d3.line()
            .x((d, i) => x(data.years[i]))
            .y((d, i) => y(data.rates[i]));

        svg.append('path')
            .datum(data.rates)
            .attr('fill', 'none')
            .attr('stroke', '#0074D9')
            .attr('stroke-width', 3)
            .attr('d', line);

        // data points
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

        // campaign acts shaded period
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

        // prison act marker      
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
                
                const textX = x(actYear);
                const textOffset = textX > width - 100 ? -8 : 8; 
                const yPosition = 40 + (0 % 3) * 20;
                const rotation = textX > width - 100 ? `rotate(90,${textX + textOffset},${yPosition})` : `rotate(-90,${textX + textOffset},${yPosition})`;
                
                svg.append('text')
                    .attr('x', textX + textOffset)
                    .attr('y', yPosition)
                    .attr('transform', rotation)
                    .style('font-size', '11px')
                    .style('font-weight', 'bold')
                    .style('fill', '#FF4136')
                    .style('text-anchor', 'start')
                    .text(actInfo.title.length > 15 ? actInfo.title.substring(0, 15) + '...' : actInfo.title);
            }
        }

        // campaign acts markers
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
                    
                    const textX = x(act.year);
                    const textOffset = textX > width - 100 ? -8 : 8;
                    const yPosition = 40 + (idx % 3) * 20; 
                    const rotation = textX > width - 100 ? `rotate(90,${textX + textOffset},${yPosition})` : `rotate(-90,${textX + textOffset},${yPosition})`;
                    
                    svg.append('text')
                        .attr('x', textX + textOffset)
                        .attr('y', yPosition)
                        .attr('fill', '#0074D9')
                        .attr('transform', rotation)
                        .style('font-size', '11px')
                        .style('font-weight', 'bold')
                        .style('text-anchor', 'start')
                        .text(act.title.length > 15 ? act.title.substring(0, 15) + '...' : act.title);
                }
            });
        }

        // transportation acts markers
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
                    
                    const textX = x(act.year);
                    const textOffset = textX > width - 100 ? -8 : 8;
                    const yPosition = 40 + (idx % 3) * 20; 
                    const rotation = textX > width - 100 ? `rotate(90,${textX + textOffset},${yPosition})` : `rotate(-90,${textX + textOffset},${yPosition})`;
                    
                    svg.append('text')
                        .attr('x', textX + textOffset)
                        .attr('y', yPosition)
                        .attr('fill', '#2ECC40')
                        .attr('transform', rotation)
                        .style('font-size', '11px')
                        .style('font-weight', 'bold')
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
        let hisclassDetail = '';
        if (groupBy === 'hisclass') {
            const cb = document.getElementById('hisclass-detail-checkbox');
            if (cb && cb.checked) {
                hisclassDetail = '&hisclass_detail=1';
            }
        }
        fetch(`/api/bar_data?group_by=${groupBy}&start_year=${startYear}&end_year=${endYear}&exclude_death=${excludeDeath}${hisclassDetail}`)
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

        // determine if social class
        let isSocialClass = false;
        let isDetailedSocialClass = false;
        if (barGroupbySelect && barGroupbySelect.value === 'hisclass') {
            isSocialClass = true;
            const cb = document.getElementById('hisclass-detail-checkbox');
            if (cb && cb.checked) {
                isDetailedSocialClass = true;
            }
        }

        // order to 1-12
        let groups = data.groups;
        if (isDetailedSocialClass) {
            let socialClassOrder = [
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'
            ];
            groups = socialClassOrder.filter(sc => groups.includes(sc));
        }

        // create a container to implement horizontal layout
        const container = d3.select('#bar-chart')
            .append('div')
            .style('display', 'flex')
            .style('justify-content', 'space-between')
            .style('align-items', 'flex-start')
            .style('width', '100%')
            .style('max-width', '1200px')
            .style('margin', '0 auto');
            
        // left spacer
        const leftSpacer = container.append('div')
            .style('width', '250px')
            .style('flex-shrink', '0');
            
        const chartContainer = container.append('div')
            .style('flex', '1')
            .style('display', 'flex')
            .style('justify-content', 'center');
        
        const margin = {top: 40, right: 40, bottom: 80, left: 120};
        const width = 600 - margin.left - margin.right;
        const height = Math.max(400, groups.length * 50) - margin.top - margin.bottom;
        
        const svg = chartContainer
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // y axis
        const y = d3.scaleBand()
            .domain(groups)
            .range([0, height])
            .padding(0.1);
        svg.append('g')
            .call(d3.axisLeft(y));

        // x axis
        const x = d3.scaleLinear()
            .domain([0, 1])
            .range([0, width]);
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).tickFormat(d3.format('.0%')));

        // x axis label
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height + margin.bottom - 25)
            .attr('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('font-weight', 'bold')
            .text('Proportion');

        // y axis label
        svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -height / 2)
            .attr('y', -margin.left + 20)
            .attr('text-anchor', 'middle')
            .style('font-size', '14px')
            .style('font-weight', 'bold')
            .text(data.group_by === 'offence_category' ? 'Offence Category' : 'Social Class');

        // stacked data
        const stack = d3.stack()
            .keys(data.punishment_categories)
            .value((d, key) => d[key] || 0);

        const transformedData = groups.map(group => {
            const row = {group: group};
            data.punishment_categories.forEach(cat => {
                row[cat] = (data.data && data.data[group] && data.data[group][cat]) || 0;
            });
            return row;
        });
        
        const stackedData = stack(transformedData);

        // color scale
        const color = d3.scaleOrdinal()
            .domain(data.punishment_categories)
            .range(d3.schemeSet2);

        // draw
        const groupsG = svg.selectAll('.group')
            .data(stackedData)
            .enter()
            .append('g')
            .attr('class', 'group')
            .attr('fill', d => color(d.key));

        groupsG.selectAll('rect')
            .data(d => d)
            .enter()
            .append('rect')
            .attr('x', d => Math.min(x(d[0]), x(d[1])))
            .attr('y', d => y(d.data.group))
            .attr('width', d => Math.abs(x(d[1]) - x(d[0])))
            .attr('height', y.bandwidth())
            .on('mouseover', function(e, d) {
                d3.select(this)
                    .attr('opacity', 0.8)
                    .attr('stroke', '#000')
                    .attr('stroke-width', 1);
                // In D3 stacked bar chart, d is [d0, d1] array, not an object with key
                // We need to get the punishment type from the parent group
                const parentGroup = d3.select(this.parentNode);
                const parentData = parentGroup.datum();
                const punishment = parentData.key || '';
                showBarTooltip(e, d.data.group, punishment, d[1] - d[0]);
            })
            .on('mouseout', function() {
                d3.select(this)
                    .attr('opacity', 1)
                    .attr('stroke', 'none');
                hideBarTooltip();
            });

        // right container for legend and notes
        const rightContainer = container.append('div')
            .style('width', '250px')
            .style('flex-shrink', '0')
            .style('margin-left', '20px');

        // legend
        const legend = rightContainer.append('div')
            .style('margin-bottom', '20px');
        legend.append('div')
            .style('font-weight', 'bold')
            .style('margin-bottom', '8px')
            .text('Punishment Categories');

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

        // detailed social class
        if (isDetailedSocialClass) {
            const socialClassTable = rightContainer.append('table')
                .attr('class', 'social-class-table')
                .style('margin-top', '24px')
                .style('border-collapse', 'collapse')
                .style('font-size', '12px');
            socialClassTable.append('caption')
                .style('caption-side', 'top')
                .style('font-weight', 'bold')
                .style('margin-bottom', '6px')
                .text('Social Class Codes (HISCLASS)');
            const tbody = socialClassTable.append('tbody');
            const socialClassMeanings = [
                '1: Higher managers',
                '2: Higher professionals',
                '3: Lower managers',
                '4: Lower professionals; higher and middle clerical and sales personnel',
                '5: Lower clerical and sales personnel',
                '6: Foremen',
                '7: Medium-skilled workers',
                '8: Farmers and fishermen',
                '9: Lower-skilled workers',
                '10: Lower-skilled farm workers',
                '11: Unskilled workers',
                '12: Unskilled farm workers'
            ];
            socialClassMeanings.forEach(row => {
                const tr = tbody.append('tr');
                const [code, desc] = row.split(': ');
                tr.append('td')
                    .style('border', '1px solid #ccc')
                    .style('padding', '2px 6px')
                    .style('text-align', 'center')
                    .text(code);
                tr.append('td')
                    .style('border', '1px solid #ccc')
                    .style('padding', '2px 6px')
                    .style('text-align', 'left')
                    .text(desc);
            });
        }
    }

    function updateImprisonChart() {
        const start = imprisonYearStartSelect.value;
        const end = imprisonYearEndSelect.value;
        const analysis = imprisonAnalysisSelect.value;
        // total average for avg_sentence and violent_crime
        const showAverage = (analysis === 'avg_sentence' || analysis === 'violent_crime') && imprisonShowAverageCheckbox.checked ? 1 : 0;
        if (parseInt(start) > parseInt(end)) return;
        fetch(`/api/imprison_data?start_year=${start}&end_year=${end}&analysis_type=${analysis}&show_average=${showAverage}`)
            .then(res => res.json())
            .then(data => {
                drawImprisonChart(data);
            });
    }

    function drawImprisonChart(data) {
        d3.select('#imprison-chart').selectAll('*').remove();
        
        const violentCrimePanel = document.getElementById('violent-crime-panel');
        if (violentCrimePanel) {
            if (data.type === 'violent_crime') {
                violentCrimePanel.style.display = 'block';
            } else {
                violentCrimePanel.style.display = 'none';
            }
        }
        
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
            
            // x axis
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
            
            // y axis
            const y = d3.scaleLinear()
                .domain([0, d3.max(data.values)])
                .nice()
                .range([height, 0]);
            svg.append('g')
                .call(d3.axisLeft(y).tickFormat(d => d.toFixed(2) + ' yrs'));

            // x axis label
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', height + margin.bottom - 25)
                .attr('text-anchor', 'middle')
                .style('font-size', '14px')
                .style('font-weight', 'bold')
                .text(getXAxisLabel(data.type));

            // y axis label
            svg.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('x', -height / 2)
                .attr('y', -margin.left + 20)
                .attr('text-anchor', 'middle')
                .style('font-size', '14px')
                .style('font-weight', 'bold')
                .text('Average Sentence (Years)');
            
            // color scheme
            const colorSchemes = {
                'avg_sentence': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'],
                'theft_value': ['#FF8C42', '#FF6B9D', '#4ECDC4', '#45B7D1'],
                'violent_crime': ['#E74C3C', '#C0392B', '#E67E22', '#D35400'],
                'habitual_vs_first': ['#3498DB', '#2980B9']
            };

            const colors = colorSchemes[data.type] || ['#0074D9'];

            // draw
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
            
            // total average dashed line
            if (data.total_average !== null && data.total_average !== undefined) {
                const averageY = y(data.total_average);
                
                // dashed line
                svg.append('line')
                    .attr('x1', 0)
                    .attr('x2', width)
                    .attr('y1', averageY)
                    .attr('y2', averageY)
                    .attr('stroke', '#FF6B6B')
                    .attr('stroke-width', 2)
                    .attr('stroke-dasharray', '6,4')
                    .attr('opacity', 0.8)
                    .on('mouseover', function(e) {
                        d3.select(this)
                            .attr('opacity', 1)
                            .attr('stroke-width', 3);
                        showAverageTooltip(e, data.total_average, data.type);
                    })
                    .on('mouseout', function() {
                        d3.select(this)
                            .attr('opacity', 0.8)
                            .attr('stroke-width', 2);
                        hideAverageTooltip();
                    });
                
                // label
                svg.append('text')
                    .attr('x', width - 10)
                    .attr('y', averageY - 8)
                    .attr('text-anchor', 'end')
                    .attr('fill', '#FF6B6B')
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bold')
                    .text(`Avg: ${data.total_average.toFixed(2)} yrs`);
            }
            
            // violent crime average line (only for violent_crime type)
            if (data.type === 'violent_crime' && data.categories.length > 0 && data.violent_average !== undefined) {
                // Use the total average calculated by backend
                const violentAverage = data.violent_average;
                const violentAverageY = y(violentAverage);
                
                // violent crime average dashed line
                svg.append('line')
                    .attr('x1', 0)
                    .attr('x2', width)
                    .attr('y1', violentAverageY)
                    .attr('y2', violentAverageY)
                    .attr('stroke', '#E67E22')
                    .attr('stroke-width', 2)
                    .attr('stroke-dasharray', '4,4')
                    .attr('opacity', 0.8)
                    .on('mouseover', function(e) {
                        d3.select(this)
                            .attr('opacity', 1)
                            .attr('stroke-width', 3);
                        showAverageTooltip(e, violentAverage, 'violent_crime');
                    })
                    .on('mouseout', function() {
                        d3.select(this)
                            .attr('opacity', 0.8)
                            .attr('stroke-width', 2);
                        hideAverageTooltip();
                    });
                
                // violent crime average label
                svg.append('text')
                    .attr('x', width - 10)
                    .attr('y', violentAverageY - 8)
                    .attr('text-anchor', 'end')
                    .attr('fill', '#E67E22')
                    .attr('font-size', '12px')
                    .attr('font-weight', 'bold')
                    .text(`Violent Avg: ${violentAverage.toFixed(2)} yrs`);
            }
            
            // title
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
            
            // note for shillings
            if (data.type === 'theft_value') {
                svg.append('text')
                    .attr('x', width / 2)
                    .attr('y', height + margin.bottom - 10)
                    .attr('text-anchor', 'middle')
                    .style('font-size', '12px')
                    .style('color', '#666')
                    .style('font-style', 'italic')
                    .text('Note: "s" stands for shillings');
            }
            
            // note for habitual vs first offenders
            if (data.type === 'habitual_vs_first') {
                svg.append('text')
                    .attr('x', width / 2)
                    .attr('y', height + margin.bottom - 10)
                    .attr('text-anchor', 'middle')
                    .style('font-size', '12px')
                    .style('color', '#666')
                    .style('font-style', 'italic')
                    .text('Note: Only comparing habitual offenders with their first offense');
            }
        } else {
            d3.select('#imprison-chart')
                .append('div')
                .style('text-align', 'center')
                .style('color', '#666')
                .style('font-size', '16px')
                .text(data.message || 'No data available for selected criteria');
        }
    }

    // create tooltip
    function createTooltip(id) {
        return d3.select('body').append('div')
            .attr('id', id)
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('background', '#fff')
            .style('border', '1px solid #ccc')
            .style('padding', '8px 12px')
            .style('border-radius', '4px')
            .style('pointer-events', 'none')
            .style('display', 'none');
    }

    // tooltip functions
    let imprisonTooltip = d3.select('#imprison-chart-tooltip');
    if (imprisonTooltip.empty()) {
        imprisonTooltip = createTooltip('imprison-chart-tooltip');
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

    // other tooltip
    const tooltip = createTooltip('line-chart-tooltip');

    function showTooltip(event, year, rate, count) {
        tooltip.style('display', 'block')
            .html(`<b>Year:</b> ${year}<br><b>Rate:</b> ${(rate*100).toFixed(2)}%<br><b>Count:</b> ${count}`)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    function hideTooltip() {
        tooltip.style('display', 'none');
    }

    let barTooltip = createTooltip('bar-chart-tooltip');

    function showBarTooltip(event, group, punishment, rate) {
        let groupLabel = 'Group';
        if (barGroupbySelect && barGroupbySelect.value === 'offence_category') {
            groupLabel = 'Offence';
        }
        barTooltip.style('display', 'block')
            .html(`<b>${groupLabel}:</b> ${group}<br><b>Punishment:</b> ${punishment}<br><b>Rate:</b> ${(rate * 100).toFixed(2)}%`)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    function hideBarTooltip() {
        barTooltip.style('display', 'none');
    }

    // new tooltip functions for average
    let averageTooltip = createTooltip('imprison-average-tooltip');

    function showAverageTooltip(event, average, analysisType) {
        let label = 'Average Sentence';
        if (analysisType === 'violent_crime') {
            label = 'Violent Crime Average Sentence';
        }
        averageTooltip.style('display', 'block')
            .html(`<b>${label}:</b> ${average.toFixed(2)} years`)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    }

    function hideAverageTooltip() {
        averageTooltip.style('display', 'none');
    }
});
