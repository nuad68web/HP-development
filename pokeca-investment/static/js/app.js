// ポケカ投資分析ツール - Frontend JS

let trendChart = null;
let rankingData = {};
let currentPeriod = "1w";
let selectedItemId = null;

// DOM Elements - Search tab
const researchBtn = document.getElementById("research-btn");
const cardNameInput = document.getElementById("card-name");
const categorySelect = document.getElementById("category");
const maxPriceInput = document.getElementById("max-price");
const statusEl = document.getElementById("status");
const loadingEl = document.getElementById("loading");
const cardDetailEl = document.getElementById("card-detail");
const rankingsEl = document.getElementById("rankings");

// DOM Elements - Portfolio tab
const addCardBtn = document.getElementById("add-card-btn");
const addModal = document.getElementById("add-modal");
const modalClose = document.getElementById("modal-close");
const modalCancel = document.getElementById("modal-cancel");
const modalSubmit = document.getElementById("modal-submit");
const acInput = document.getElementById("ac-input");
const acDropdown = document.getElementById("ac-dropdown");
const acSelected = document.getElementById("ac-selected");
const acClear = document.getElementById("ac-clear");
const purchasePriceInput = document.getElementById("purchase-price-input");

// ========== メインタブ切替 ==========
document.querySelectorAll(".main-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".main-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");

        document.querySelectorAll(".tab-content").forEach((c) => c.classList.add("hidden"));
        document.getElementById(`tab-${tab.dataset.tab}`).classList.remove("hidden");

        if (tab.dataset.tab === "portfolio") {
            loadPortfolio();
        }
    });
});

// ========== カードを探す（既存機能） ==========
researchBtn.addEventListener("click", startResearch);
cardNameInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") startResearch();
});

document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        currentPeriod = tab.dataset.period;
        renderRankingTable(rankingData[currentPeriod] || []);
    });
});

async function startResearch() {
    const cardName = cardNameInput.value.trim();
    const category = categorySelect.value || null;
    const maxPrice = maxPriceInput.value ? parseInt(maxPriceInput.value) : null;

    researchBtn.disabled = true;
    loadingEl.classList.remove("hidden");
    statusEl.classList.add("hidden");
    cardDetailEl.classList.add("hidden");
    rankingsEl.classList.add("hidden");

    try {
        showStatus("info", "メルカリ・スニダンからデータを収集中...");
        const researchResp = await fetch("/api/research", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ card_name: cardName || null, category }),
        });
        const researchData = await researchResp.json();

        if (!researchResp.ok) {
            throw new Error(researchData.error || "調査に失敗しました");
        }

        showStatus("success", researchData.message);

        if (cardName) {
            await showCardDetail(cardName, category);
        } else {
            await showRankings(category, maxPrice);
        }
    } catch (err) {
        showStatus("error", `エラー: ${err.message}`);
    } finally {
        researchBtn.disabled = false;
        loadingEl.classList.add("hidden");
    }
}

async function showCardDetail(cardName, category) {
    const params = new URLSearchParams({ q: cardName });
    if (category) params.set("category", category);

    const resp = await fetch(`/api/search?${params}`);
    const data = await resp.json();

    if (!data.found || data.items.length === 0) {
        showStatus("info", `「${cardName}」のデータが見つかりませんでした。データが蓄積されるまでお待ちください。`);
        return;
    }

    cardDetailEl.classList.remove("hidden");
    document.getElementById("card-detail-title").textContent = `「${cardName}」の分析結果`;

    const item = data.items[0];

    renderChangeCard("change-1w", item.change_1w);
    renderChangeCard("change-1m", item.change_1m);
    renderChangeCard("change-1y", item.change_1y);

    if (item.monthly_trend && item.monthly_trend.length > 0) {
        renderTrendChart(item.monthly_trend, item.name);
    } else {
        const chartCanvas = document.getElementById("trend-chart");
        if (trendChart) trendChart.destroy();
        const ctx = chartCanvas.getContext("2d");
        ctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
        ctx.fillStyle = "#666";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("月次トレンドデータが不足しています", chartCanvas.width / 2, chartCanvas.height / 2);
    }

    const sourcesEl = document.getElementById("card-sources");
    sourcesEl.innerHTML = "<h3 style='color:#999;margin-bottom:12px'>ソース別データ</h3>";
    data.items.forEach((it) => {
        const latest = it.latest_price;
        const priceText = latest ? `¥${latest.price.toLocaleString()}` : "価格なし";
        const escapedName = escapeHtml(it.name);
        const imgTag = it.image_url ? `<img src="${escapeHtml(it.image_url)}" alt="">` : "";
        sourcesEl.innerHTML += `
            <div class="source-item">
                ${imgTag}
                <div>
                    <strong>${escapedName}</strong><br>
                    <span class="source-badge ${it.source}">${it.source === "mercari" ? "メルカリ" : "スニダン"}</span>
                    <span class="category-badge ${it.category}">${it.category === "psa10" ? "PSA 10" : "未開封BOX"}</span>
                    <span style="margin-left:8px;color:#ffd700">${priceText}</span>
                </div>
            </div>
        `;
    });
}

function renderChangeCard(elementId, changeData) {
    const card = document.getElementById(elementId);
    const valueEl = card.querySelector(".change-value");
    const detailEl = card.querySelector(".change-detail");

    if (!changeData) {
        valueEl.textContent = "---";
        valueEl.className = "change-value neutral";
        detailEl.textContent = "データ不足";
        return;
    }

    const sign = changeData.change >= 0 ? "+" : "";
    valueEl.textContent = `${sign}${changeData.change_pct}%`;
    valueEl.className = `change-value ${changeData.change >= 0 ? "positive" : "negative"}`;
    detailEl.textContent = `¥${changeData.old_price.toLocaleString()} → ¥${changeData.new_price.toLocaleString()} (${sign}¥${changeData.change.toLocaleString()})`;
}

function renderTrendChart(trendData, itemName) {
    const ctx = document.getElementById("trend-chart").getContext("2d");
    if (trendChart) trendChart.destroy();

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: trendData.map((t) => t.month),
            datasets: [
                {
                    label: "平均価格",
                    data: trendData.map((t) => t.avg_price),
                    borderColor: "#ffd700",
                    backgroundColor: "rgba(255, 215, 0, 0.1)",
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: "#ffd700",
                },
                {
                    label: "最高価格",
                    data: trendData.map((t) => t.max_price),
                    borderColor: "rgba(76, 175, 80, 0.5)",
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 2,
                },
                {
                    label: "最低価格",
                    data: trendData.map((t) => t.min_price),
                    borderColor: "rgba(244, 67, 54, 0.5)",
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.3,
                    pointRadius: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${itemName} - 月次価格推移`,
                    color: "#e0e0e0",
                    font: { size: 14 },
                },
                legend: { labels: { color: "#999" } },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ¥${ctx.parsed.y.toLocaleString()}`,
                    },
                },
            },
            scales: {
                x: { ticks: { color: "#666" }, grid: { color: "#1e2540" } },
                y: {
                    ticks: { color: "#666", callback: (v) => `¥${v.toLocaleString()}` },
                    grid: { color: "#1e2540" },
                },
            },
        },
    });
}

async function showRankings(category, maxPrice) {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (maxPrice) params.set("max_price", maxPrice);

    const resp = await fetch(`/api/top/all?${params}`);
    rankingData = await resp.json();

    rankingsEl.classList.remove("hidden");
    currentPeriod = "1w";
    document.querySelectorAll(".tab").forEach((t) => {
        t.classList.toggle("active", t.dataset.period === "1w");
    });
    renderRankingTable(rankingData["1w"] || []);
}

function renderRankingTable(items) {
    const tbody = document.getElementById("ranking-body");
    const noDataMsg = document.getElementById("no-data-msg");
    const table = document.getElementById("ranking-table");

    if (!items || items.length === 0) {
        table.classList.add("hidden");
        noDataMsg.classList.remove("hidden");
        return;
    }

    table.classList.remove("hidden");
    noDataMsg.classList.add("hidden");

    tbody.innerHTML = items
        .map((item, i) => {
            const sign = item.price_change >= 0 ? "+" : "";
            const changeClass = item.price_change >= 0 ? "positive" : "negative";
            const categoryLabel = item.category === "psa10" ? "PSA 10" : "未開封BOX";
            const sourceLabel = item.source === "mercari" ? "メルカリ" : "スニダン";
            const imgTag = item.image_url ? `<img src="${escapeHtml(item.image_url)}" alt="">` : "-";

            return `
            <tr>
                <td>${i + 1}</td>
                <td>${imgTag}</td>
                <td>${escapeHtml(item.name)}</td>
                <td><span class="category-badge ${item.category}">${categoryLabel}</span></td>
                <td><span class="source-badge ${item.source}">${sourceLabel}</span></td>
                <td>¥${(item.new_price || 0).toLocaleString()}</td>
                <td class="${changeClass}">${sign}¥${(item.price_change || 0).toLocaleString()}</td>
                <td class="${changeClass}">${sign}${item.change_pct || 0}%</td>
            </tr>
        `;
        })
        .join("");
}

function showStatus(type, message) {
    statusEl.className = `status ${type}`;
    statusEl.textContent = message;
    statusEl.classList.remove("hidden");
}

// ========== カードを管理する（ポートフォリオ） ==========

async function loadPortfolio() {
    const resp = await fetch("/api/portfolio");
    const data = await resp.json();
    renderPortfolioSummary(data.summary);
    renderPortfolioGrid(data.items);
}

function renderPortfolioSummary(summary) {
    document.getElementById("pf-count").textContent = summary.count;
    document.getElementById("pf-investment").textContent = `¥${summary.total_investment.toLocaleString()}`;
    document.getElementById("pf-current").textContent = summary.total_current != null ? `¥${summary.total_current.toLocaleString()}` : "---";

    const plEl = document.getElementById("pf-pl");
    if (summary.total_profit_loss != null) {
        const sign = summary.total_profit_loss >= 0 ? "+" : "";
        plEl.textContent = `${sign}¥${summary.total_profit_loss.toLocaleString()} (${sign}${summary.total_profit_loss_pct}%)`;
        plEl.className = `summary-value ${summary.total_profit_loss >= 0 ? "positive" : "negative"}`;
    } else {
        plEl.textContent = "---";
        plEl.className = "summary-value";
    }
}

function renderPortfolioGrid(items) {
    const grid = document.getElementById("portfolio-grid");
    const emptyMsg = document.getElementById("portfolio-empty");

    if (!items || items.length === 0) {
        grid.innerHTML = "";
        grid.appendChild(emptyMsg);
        emptyMsg.classList.remove("hidden");
        return;
    }

    emptyMsg.classList.add("hidden");

    grid.innerHTML = items
        .map((item) => {
            const currentText = item.current_price != null ? `¥${item.current_price.toLocaleString()}` : "価格未取得";
            let plHtml = "";
            if (item.profit_loss != null) {
                const sign = item.profit_loss >= 0 ? "+" : "";
                const plClass = item.profit_loss >= 0 ? "positive" : "negative";
                plHtml = `<span class="pf-pl ${plClass}">${sign}¥${item.profit_loss.toLocaleString()} (${sign}${item.profit_loss_pct}%)</span>`;
            } else {
                plHtml = `<span class="pf-pl neutral">損益不明</span>`;
            }

            const categoryLabel = item.category === "psa10" ? "PSA 10" : "未開封BOX";
            const sourceLabel = item.source === "mercari" ? "メルカリ" : "スニダン";
            const escapedName = escapeHtml(item.name);
            const imgSrc = item.image_url ? escapeHtml(item.image_url) : "";

            return `
            <div class="portfolio-card">
                <button class="pf-delete-btn" data-id="${item.portfolio_id}" title="削除">&times;</button>
                <div class="pf-card-img">
                    ${imgSrc ? `<img src="${imgSrc}" alt="${escapedName}">` : `<div class="pf-no-img">NO IMAGE</div>`}
                </div>
                <div class="pf-card-body">
                    <div class="pf-card-name">${escapedName}</div>
                    <div class="pf-card-badges">
                        <span class="category-badge ${item.category}">${categoryLabel}</span>
                        <span class="source-badge ${item.source}">${sourceLabel}</span>
                    </div>
                    <div class="pf-card-prices">
                        <div class="pf-price-row">
                            <span class="pf-price-label">購入額</span>
                            <span class="pf-price-value">¥${item.purchase_price.toLocaleString()}</span>
                        </div>
                        <div class="pf-price-row">
                            <span class="pf-price-label">現在相場</span>
                            <span class="pf-price-value">${currentText}</span>
                        </div>
                    </div>
                    <div class="pf-card-pl">${plHtml}</div>
                </div>
            </div>
        `;
        })
        .join("");

    // 削除ボタン
    grid.querySelectorAll(".pf-delete-btn").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
            e.stopPropagation();
            if (!confirm("このカードをポートフォリオから削除しますか？")) return;
            const id = btn.dataset.id;
            await fetch(`/api/portfolio/${id}`, { method: "DELETE" });
            loadPortfolio();
        });
    });
}

// ========== モーダル ==========

addCardBtn.addEventListener("click", () => {
    addModal.classList.remove("hidden");
    acInput.value = "";
    purchasePriceInput.value = "";
    selectedItemId = null;
    acSelected.classList.add("hidden");
    acDropdown.classList.add("hidden");
    acInput.focus();
});

modalClose.addEventListener("click", closeModal);
modalCancel.addEventListener("click", closeModal);
addModal.addEventListener("click", (e) => {
    if (e.target === addModal) closeModal();
});

function closeModal() {
    addModal.classList.add("hidden");
}

// ========== オートコンプリート ==========

let acTimer = null;
acInput.addEventListener("input", () => {
    clearTimeout(acTimer);
    const q = acInput.value.trim();
    if (q.length < 1) {
        acDropdown.classList.add("hidden");
        return;
    }
    acTimer = setTimeout(() => fetchAutocomplete(q), 300);
});

acInput.addEventListener("keydown", (e) => {
    if (e.key === "Escape") acDropdown.classList.add("hidden");
});

async function fetchAutocomplete(query) {
    const resp = await fetch(`/api/items/autocomplete?q=${encodeURIComponent(query)}`);
    const items = await resp.json();

    if (items.length === 0) {
        acDropdown.innerHTML = `<div class="ac-item ac-empty">候補が見つかりません</div>`;
        acDropdown.classList.remove("hidden");
        return;
    }

    acDropdown.innerHTML = items
        .map((item) => {
            const categoryLabel = item.category === "psa10" ? "PSA 10" : "未開封BOX";
            const sourceLabel = item.source === "mercari" ? "メルカリ" : "スニダン";
            const priceText = item.current_price != null ? `¥${item.current_price.toLocaleString()}` : "";
            const imgSrc = item.image_url ? escapeHtml(item.image_url) : "";

            return `
            <div class="ac-item" data-id="${item.id}" data-name="${escapeHtml(item.name)}" data-img="${imgSrc}" data-cat="${categoryLabel}" data-src="${sourceLabel}" data-price="${priceText}">
                ${imgSrc ? `<img src="${imgSrc}" alt="">` : `<div class="ac-item-noimg"></div>`}
                <div class="ac-item-info">
                    <div class="ac-item-name">${escapeHtml(item.name)}</div>
                    <div class="ac-item-meta">${categoryLabel} / ${sourceLabel} ${priceText}</div>
                </div>
            </div>
        `;
        })
        .join("");

    acDropdown.classList.remove("hidden");

    acDropdown.querySelectorAll(".ac-item[data-id]").forEach((el) => {
        el.addEventListener("click", () => {
            selectedItemId = parseInt(el.dataset.id);
            document.getElementById("ac-selected-name").textContent = el.dataset.name;
            document.getElementById("ac-selected-meta").textContent = `${el.dataset.cat} / ${el.dataset.src} ${el.dataset.price}`;
            const imgEl = document.getElementById("ac-selected-img");
            if (el.dataset.img) {
                imgEl.src = el.dataset.img;
                imgEl.style.display = "block";
            } else {
                imgEl.style.display = "none";
            }
            acSelected.classList.remove("hidden");
            acInput.style.display = "none";
            acDropdown.classList.add("hidden");
        });
    });
}

acClear.addEventListener("click", () => {
    selectedItemId = null;
    acSelected.classList.add("hidden");
    acInput.style.display = "block";
    acInput.value = "";
    acInput.focus();
});

// 入力欄以外クリックでドロップダウン閉じる
document.addEventListener("click", (e) => {
    if (!e.target.closest(".autocomplete-wrapper")) {
        acDropdown.classList.add("hidden");
    }
});

// ========== 追加送信 ==========

modalSubmit.addEventListener("click", async () => {
    if (!selectedItemId) {
        alert("カードを選択してください");
        return;
    }
    const price = parseInt(purchasePriceInput.value);
    if (!price || price <= 0) {
        alert("購入額を正しく入力してください");
        return;
    }

    modalSubmit.disabled = true;
    try {
        const resp = await fetch("/api/portfolio", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_id: selectedItemId, purchase_price: price }),
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.error);
        closeModal();
        loadPortfolio();
    } catch (err) {
        alert(`エラー: ${err.message}`);
    } finally {
        modalSubmit.disabled = false;
    }
});

// ========== ユーティリティ ==========

function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
