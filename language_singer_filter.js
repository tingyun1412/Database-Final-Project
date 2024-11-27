let playlistData = [];  // 儲存所有歌曲數據
let currentChart = null;  // 當前顯示的圖表

// 處理檔案上傳
function handleUserUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        processCSVData(text);
    };
    reader.readAsText(file);
}

// 處理 CSV 數據
function processCSVData(csvText) {
    const rows = csvText.split("\n").map(row => row.trim().split(","));
    const headers = rows.shift();

    // 清空現有數據
    playlistData = [];
    
    // 統計數據
    const languageCounts = {};
    const singerCounts = {};

    // 處理每一行數據
    rows.forEach(row => {
        if (row.length < 3) return; // 跳過不完整的行
        
        const [songName, singerName, language] = row.map(item => item.trim());
        
        // 確保數據完整性
        if (!songName || !singerName || !language) return;

        // 添加到數據集
        playlistData.push({ songName, singerName, language });
        
        // 更新統計
        languageCounts[language] = (languageCounts[language] || 0) + 1;
        singerCounts[singerName] = (singerCounts[singerName] || 0) + 1;
    });

    // 更新側邊欄表格
    updateSidebar();
    
    // 更新過濾選項
    updateFilterOptions(languageCounts, singerCounts);
    
    // 初始顯示語言分布圖表
    showAnalysis('language');
}

// 更新側邊欄
function updateSidebar() {
    const sidebar = document.querySelector('.sidebar');
    let html = `
        Song Name   Singer Name   Language
        ----------- ------------- ----------
    `;
    
    playlistData.forEach(item => {
        html += `\n${item.songName.padEnd(12)} ${item.singerName.padEnd(14)} ${item.language}`;
    });
    
    sidebar.innerHTML = html;
}

// 更新過濾選項
function updateFilterOptions(languageCounts, singerCounts) {
    // 更新語言選項
    const languageOptions = document.getElementById('language-options');
    languageOptions.innerHTML = '<h3>語言：</h3>';
    Object.entries(languageCounts).forEach(([language, count]) => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = language;
        checkbox.addEventListener('change', updatePlaylist);
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(`${language} (${count})`));
        languageOptions.appendChild(label);
    });

    // 更新歌手選項
    const singerOptions = document.getElementById('singer-options');
    singerOptions.innerHTML = '<h3>歌手：</h3>';
    Object.entries(singerCounts).forEach(([singer, count]) => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = singer;
        checkbox.addEventListener('change', updatePlaylist);
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(`${singer} (${count})`));
        singerOptions.appendChild(label);
    });
}

// 更新播放清單
function updatePlaylist() {
    const selectedLanguages = Array.from(document.querySelectorAll('#language-options input:checked'))
        .map(cb => cb.value);
    const selectedSingers = Array.from(document.querySelectorAll('#singer-options input:checked'))
        .map(cb => cb.value);

    const filteredSongs = playlistData.filter(song => 
        (selectedLanguages.length === 0 || selectedLanguages.includes(song.language)) &&
        (selectedSingers.length === 0 || selectedSingers.includes(song.singerName))
    );

    const songList = document.querySelector('.song-list');
    songList.innerHTML = '';
    filteredSongs.forEach(song => {
        const div = document.createElement('div');
        div.innerHTML = `${song.songName} - ${song.singerName} (${song.language})`;
        songList.appendChild(div);
    });
}

// 顯示分析圖表
function showAnalysis(type) {
    const ctx = document.querySelector('.chart canvas').getContext('2d');
    
    if (currentChart) {
        currentChart.destroy();
    }

    const data = type === 'language'
        ? playlistData.reduce((acc, song) => {
            acc[song.language] = (acc[song.language] || 0) + 1;
            return acc;
        }, {})
        : playlistData.reduce((acc, song) => {
            acc[song.singerName] = (acc[song.singerName] || 0) + 1;
            return acc;
        }, {});

    currentChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', 
                    '#4BC0C0', '#9966FF', '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: type === 'language' ? '語言分布' : '歌手分布'
                },
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// 建立播放清單
function createPlaylistAndRedirect() {
    const selectedLanguages = Array.from(document.querySelectorAll('#language-options input:checked'))
        .map(cb => cb.value);
    const selectedSingers = Array.from(document.querySelectorAll('#singer-options input:checked'))
        .map(cb => cb.value);

    if (selectedLanguages.length === 0 && selectedSingers.length === 0) {
        alert('請至少選擇一個語言或歌手');
        return;
    }

    const playlist = playlistData.filter(song => 
        (selectedLanguages.length === 0 || selectedLanguages.includes(song.language)) &&
        (selectedSingers.length === 0 || selectedSingers.includes(song.singerName))
    );

    localStorage.setItem('playlist', JSON.stringify(playlist));
    window.location.href = 'newplaylist.html';
}

// 當頁面載入時初始化
window.onload = function() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.csv';
    fileInput.onchange = handleUserUpload;
    document.querySelector('.content').insertBefore(fileInput, document.querySelector('.buttons'));
};