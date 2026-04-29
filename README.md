# 個人代理型知識庫 (Personal Agentic Knowledge Base / LLM-Wiki)

這個儲存庫是一個由 AI 維護、完美相容於 Obsidian 的個人知識庫。它專為 Gemini CLI（或其他支援 Agent Skills 的 LLM 工具）設計，基於 Andrej Karpathy 的 LLM-Wiki 設計模式，並透過現代化個人知識管理 (PKM) 架構進行了全面升級。

## 架構哲學 (Architecture Philosophy)

- **AI 擔任圖書管理員 (Librarian)**：LLM 負責閱讀、編譯、建立交叉連結以及進行知識庫的健康檢查 (Lint)。
- **人類擔任資訊策展人 (Curator)**：人類負責篩選高品質的原始資料、提出問題，並裁決高階的知識衝突。
- **雙向連結 (Bi-directional Linking)**：所有知識節點皆使用 Obsidian 風格的 `[[雙向連結]]` 進行串接，徹底捨棄傳統相對路徑。
- **元資料解耦 (Metadata Decoupling)**：檔案屬性（狀態、標籤、日期、來源）嚴格透過 YAML Frontmatter 進行統一管理。

## 目錄結構 (Directory Structure)

- `raw/`：單一真相來源 (Source of Truth)。存放不可變更的原始素材（PDF、Markdown 文章）。此處檔案的狀態為 `status: "ingested"`。
- `wiki/`：動態的知識圖譜。存放由 LLM 編譯的實體、概念與綜合解析頁面。此處檔案的狀態為 `status: "active"`、`status: "archived"` 或 `status: "stub"`。
- `wiki/index.md`：全局知識目錄 (Map of Content, MOC)。僅在建立新實體文章或新主題分類時才會更新。
- `wiki/log.md`：具備圖譜追溯性的時序操作日誌。
- `.gemini/skills/karpathy-llm-wiki/`：系統提示詞、Agent 執行守則 (`SKILL.md`) 以及相關的 Markdown 格式範本。

## 核心工作流 (Core Workflows / 實戰指令指南)

在你的 AI 終端機或 IDE（如 Gemini CLI 或 Antigravity）中，你可以完全使用自然語言與系統溝通。以下是三大核心工作流的具體使用情境與進階指令範例：

### 1. 攝取 (Ingest)：知識的吸收與連鎖更新
**使用情境**：你剛看完一篇極具啟發性的 arXiv 論文或財報，想將其納入你的數位大腦。
**操作步驟**：
1. 將原始檔案（如 `DeepSeek-V3-Paper.pdf` 或整理好的 Markdown 筆記）直接放入 `raw/` 目錄。
2. 對 AI 下達 Ingest 指令。

**對話指令範例**：
- **基礎指令**：`「請 Ingest raw/ 裡面的最新論文，並將其萃取更新至 wiki 中。」`
- **進階指令 (帶有引導性)**：`「請 Ingest raw/ 裡面的 DeepSeek 論文。在編譯至 wiki 時，請特別留意它與現有 Transformer 架構的差異，並確保更新相關的 active 狀態文章。」`

**系統預期行為**：AI 會為 PDF 建立伴生代理 Markdown 檔、寫入 YAML 屬性、在 `wiki/` 中建立或更新關聯的實體文章，最後在 `log.md` 留下操作紀錄。

### 2. 查詢與封存 (Query & Archive)：知識的提取、審核與快照
**使用情境**：你需要根據過去累積的知識進行寫作或決策。為確保知識庫的品質，這是一個「兩階段」的人機協作過程：先讓 AI 檢索與草擬，經你人類大腦審核認可後，才正式建立快照。
**操作步驟**：

* **階段一：純查詢與草擬 (Drafting)**
    * **對話指令**：`「根據我的 wiki，幫我草擬一份比較 Agentic AI 與傳統 RAG 優劣勢的分析報告。請先在對話框輸出即可，不要寫入檔案。」`
    * **系統行為**：AI 僅會在畫面上提供綜合解答。此時你可以針對內容要求修改（例如：`「第二段關於 Token 消耗的觀點寫得太淺，請根據 wiki 內的數據再補充深入一點」`）。
* **階段二：審核與封存 (Commit & Archive)**
    * **對話指令**：`「這個最終版本寫得很好，我認可了。請將這份最終報告 Archive 起來，存入 wiki 目錄中。」`
    * **系統行為**：AI 會建立一個全新的 Markdown 實體檔案，寫入你剛才認可的內容，將其標記為 `status: "archived"`，最後同步更新全局目錄 `index.md` 與操作日誌 `log.md`。

### 3. 健康檢查 (Lint)：知識庫的大掃除與自動修補
**使用情境**：經過幾週的頻繁 Ingest 與手動筆記後，你懷疑知識庫裡出現了死連結、矛盾的觀點，或是遺漏的關鍵概念。建議每週執行一次。
**操作步驟**：
要求 AI 執行全面或特定範圍的 Lint 檢查。

**對話指令範例**：
- **基礎指令**：`「請幫我 Lint 整個 wiki 知識庫。自動修復破裂的雙向連結，並回報你發現的事實矛盾。」`
- **進階指令 (針對空節點)**：`「請執行 Lint。特別幫我掃描所有被頻繁引用但尚未建立實體的概念，自動幫我建立 status 為 stub 的空檔案，方便我日後研究。」`

**系統預期行為**：AI 會在背景靜默修復錯誤的 `[[雙向連結]]` 與缺失的 YAML 欄位，建立 `stub` 佔位檔案，最後在對話框中向你列出一份「需人類介入審核」的邏輯矛盾清單，並將修復結果記錄至 `log.md`。

## 環境設定與依賴 (Setup & Dependencies)

1. **知識庫視覺化 (IDE)**：強烈建議使用 **Obsidian** 開啟此專案目錄，以完美視覺化知識圖譜並順暢閱讀 Markdown 檔案。
2. **AI 工具 (AI Tooling)**：需要配置具備讀取本地 `.gemini/skills/` 能力的 AI Agent 工具（例如：搭配 Google AI Pro 的 Gemini CLI 或是 Antigravity）。
3. **版本控制 (Version Control)**：強烈建議使用 `git` 定期提交變更，以作為防護網，防止 AI 產生不可逆的幻覺擴散 (Hallucination Cascades)。