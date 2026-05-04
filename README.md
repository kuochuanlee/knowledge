# 個人代理型知識庫 (Personal Agentic Knowledge Base / LLM-Wiki)

這個儲存庫是一個由 AI 維護、完美相容於 Obsidian 的個人知識庫。它專為 Gemini CLI（或其他支援 Agent Skills 的 LLM 工具）設計，基於 Andrej Karpathy 的 LLM-Wiki 設計模式，並透過現代化個人知識管理 (PKM) 架構進行了全面升級。

## 架構哲學 (Architecture Philosophy)

- **AI 擔任圖書管理員 (Librarian)**：LLM 負責閱讀、編譯、建立交叉連結以及進行知識庫的健康檢查 (Lint)。
- **人類擔任資訊策展人 (Curator)**：人類負責篩選高品質的原始資料、提出問題，並裁決高階的知識衝突。
- **雙向連結 (Bi-directional Linking)**：所有知識節點皆使用 Obsidian 風格的 `[[雙向連結]]` 進行串接，徹底捨棄傳統相對路徑。
- **元資料解耦 (Metadata Decoupling)**：檔案屬性（狀態、標籤、日期、來源）嚴格透過 YAML Frontmatter 進行統一管理。

## 目錄結構 (Directory Structure)

| 路徑 | 說明 |
|------|------|
| `book/<書名>/` | 書籍原始 Markdown 檔案，供 split-book 切割使用 |
| `wiki/raw/` | 單一真相來源 (Source of Truth)。存放不可變更的原始素材（PDF、切割後的書籍章節、Markdown 文章）。狀態為 `status: "ingested"` |
| `wiki/` | 動態的知識圖譜。存放由 LLM 編譯的實體、概念與綜合解析頁面。狀態為 `status: "active"`、`"archived"` 或 `"stub"` |
| `wiki/index.md` | 全局知識目錄 (Map of Content, MOC)。僅在建立新實體文章或新主題分類時才會更新 |
| `wiki/log.md` | 具備圖譜追溯性的時序操作日誌 |
| `.gemini/skills/split-book/` | 書籍切割 Skill 的執行守則與 Python 腳本 |
| `.gemini/skills/karpathy-llm-wiki/` | 知識庫 Skill 的執行守則 (`SKILL.md`) 與 Markdown 格式範本 |

## 可用的 Skills

本專案提供兩個 AI Agent Skill，各司其職，形成上下游的知識處理管線：

```
書籍 (.md)                     原始素材 (raw/)                    知識文章 (wiki/)
  |                                 |                                  |
  |   [split-book]                  |   [karpathy-llm-wiki]            |
  +-------> 切割成章節 md ---------> +-------> 萃取/編譯 wiki ---------> +
            (前置處理)                         (知識建構)
```

---

## Skill 1：split-book (書籍前置切割器)

**觸發關鍵字**：`split-book <書名>`、`幫我切割書籍`、`把書拆成章節`、`預處理書籍 md 檔`

### 用途

將完整書籍的 Markdown 檔案，依照章節邊界切割成適合 RAG 處理的中等長度片段，輸出至 `wiki/raw/`。這是 Ingest 之前的前置處理步驟。

### 使用情境

你從 Kindle 或其他管道取得了一本書的完整 Markdown 檔案，單檔太大（數千行）不適合直接 Ingest，需要先拆分成章節級別的小檔。

### 操作步驟

1. 將書籍 Markdown 檔案放入 `book/<書名>/<書名>.md`。
2. 對 AI 下達切割指令。

### 對話指令範例

- **基礎指令**：`「幫我切割 book/ 裡面的《AI傳產驅動力》」`
- **進階指令**：`「split-book AI傳產驅動力，這本書用的是 PART 分篇，請以 PART 為最粗粒度來切」`

### 系統預期行為

AI 會執行一套多輪的人機協作流程：

1. **萃取標題** — 使用 `extract_headings.py` 腳本取得書籍的標題結構清單。
2. **第一輪：識別章邊界** — AI 閱讀標題清單，識別頂層章節分界，輸出一份確認表供你檢視。
3. **第二輪：逐章決策** — 依據行數判斷每個區塊要合併、保持或拆分，再次輸出決策表供你確認。
4. **執行切割** — AI 先 dry-run 確認計畫無誤，再正式執行 `split_book.py` 寫出切割檔至 `wiki/raw/`。

### 切割規則

| 行數範圍 | 決策 |
|----------|------|
| < 100 行 | 合併至相鄰章節 |
| 100 ~ 600 行 | 保持獨立 |
| > 600 行 | 進行二次切割 |

### 輸出檔案

```
wiki/raw/<書名>_0.md    -- 前言區
wiki/raw/<書名>_1.md    -- 第一個切割點
wiki/raw/<書名>_2.md    -- 第二個切割點
...
wiki/raw/<書名>_N_0.md  -- 二次切割的子段（若有超大章節）
```

---

## Skill 2：karpathy-llm-wiki (知識庫管理)

**觸發關鍵字**：`Ingest`、`新增至 wiki`、`關於...我知道什麼`、`LLM wiki`、`Karpathy wiki`

### 用途

讀取 `wiki/raw/` 中的原始資料，萃取核心概念並編譯成結構化的知識文章，存放於 `wiki/`。同時負責查詢、封存與健康檢查。

在你的 AI 終端機或 IDE（如 Gemini CLI 或 Antigravity）中，你可以完全使用自然語言與系統溝通。以下是三大核心工作流的具體使用情境與進階指令範例：

### 工作流 1：攝取 (Ingest) — 知識的吸收與連鎖更新

**使用情境**：你剛看完一篇極具啟發性的 arXiv 論文或財報，想將其納入你的數位大腦。
**操作步驟**：
1. 將原始檔案（如 `DeepSeek-V3-Paper.pdf` 或整理好的 Markdown 筆記）直接放入 `raw/` 目錄。
2. 對 AI 下達 Ingest 指令。

**對話指令範例**：
- **基礎指令**：`「請 Ingest raw/ 裡面的最新論文，並將其萃取更新至 wiki 中。」`
- **進階指令 (帶有引導性)**：`「請 Ingest raw/ 裡面的 DeepSeek 論文。在編譯至 wiki 時，請特別留意它與現有 Transformer 架構的差異，並確保更新相關的 active 狀態文章。」`

**系統預期行為**：AI 會為 PDF 建立伴生代理 Markdown 檔、寫入 YAML 屬性、在 `wiki/` 中建立或更新關聯的實體文章，最後在 `log.md` 留下操作紀錄。對於不含可萃取知識的原始資料（如封面頁、致謝詞、版權頁），AI 會自動跳過並在日誌中記錄原因。

### 工作流 2：查詢與封存 (Query & Archive) — 知識的提取、審核與快照

**使用情境**：你需要根據過去累積的知識進行寫作或決策。為確保知識庫的品質，這是一個「兩階段」的人機協作過程：先讓 AI 檢索與草擬，經你人類大腦審核認可後，才正式建立快照。
**操作步驟**：

* **階段一：純查詢與草擬 (Drafting)**
    * **對話指令**：`「根據我的 wiki，幫我草擬一份比較 Agentic AI 與傳統 RAG 優劣勢的分析報告。請先在對話框輸出即可，不要寫入檔案。」`
    * **系統行為**：AI 僅會在畫面上提供綜合解答。此時你可以針對內容要求修改（例如：`「第二段關於 Token 消耗的觀點寫得太淺，請根據 wiki 內的數據再補充深入一點」`）。
* **階段二：審核與封存 (Commit & Archive)**
    * **對話指令**：`「這個最終版本寫得很好，我認可了。請將這份最終報告 Archive 起來，存入 wiki 目錄中。」`
    * **系統行為**：AI 會建立一個全新的 Markdown 實體檔案，寫入你剛才認可的內容，將其標記為 `status: "archived"`，最後同步更新全局目錄 `index.md` 與操作日誌 `log.md`。

### 工作流 3：健康檢查 (Lint) — 知識庫的大掃除與自動修補

**使用情境**：經過幾週的頻繁 Ingest 與手動筆記後，你懷疑知識庫裡出現了死連結、矛盾的觀點，或是遺漏的關鍵概念。建議每週執行一次。
**操作步驟**：
要求 AI 執行全面或特定範圍的 Lint 檢查。

**對話指令範例**：
- **基礎指令**：`「請幫我 Lint 整個 wiki 知識庫。自動修復破裂的雙向連結，並回報你發現的事實矛盾。」`
- **進階指令 (針對空節點)**：`「請執行 Lint。特別幫我掃描所有被頻繁引用但尚未建立實體的概念，自動幫我建立 status 為 stub 的空檔案，方便我日後研究。」`

**系統預期行為**：AI 會在背景靜默修復錯誤的 `[[雙向連結]]` 與缺失的 YAML 欄位，建立 `stub` 佔位檔案，最後在對話框中向你列出一份「需人類介入審核」的邏輯矛盾清單，並將修復結果記錄至 `log.md`。

---

## 典型端到端流程 (End-to-End Workflow)

處理一本書從原始檔案到知識文章的完整流程：

```
1. 放檔案        book/AI傳產驅動力/AI傳產驅動力.md
2. split-book    「幫我切割 AI傳產驅動力」
3. 確認切割表     AI 輸出確認表，你審核切割點
4. 執行切割       wiki/raw/AI傳產驅動力_0.md ~ _N.md
5. Ingest        「請 Ingest raw/ 裡的 AI傳產驅動力 系列檔案」
6. AI 編譯        萃取概念 → wiki/ 知識文章（自動跳過封面/致謝等無知識價值的切割檔）
7. 查詢           「關於 AI 在傳統產業的應用，我知道些什麼？」
```

## 環境設定與依賴 (Setup & Dependencies)

1. **知識庫視覺化 (IDE)**：強烈建議使用 **Obsidian** 開啟此專案目錄，以完美視覺化知識圖譜並順暢閱讀 Markdown 檔案。
2. **AI 工具 (AI Tooling)**：需要配置具備讀取本地 `.gemini/skills/` 能力的 AI Agent 工具（例如：搭配 Google AI Pro 的 Gemini CLI 或是 Antigravity）。
3. **版本控制 (Version Control)**：強烈建議使用 `git` 定期提交變更，以作為防護網，防止 AI 產生不可逆的幻覺擴散 (Hallucination Cascades)。

---

## 實用腳本 (Utility Scripts)

本專案在 `scripts/` 目錄下提供了一些輔助腳本，方便日常知識管理操作：

### 1. 網頁轉 Markdown (`web_to_md.py`)

**用途**：將指定的網頁主體內容抓取並轉換為 Markdown 格式，預設儲存至 `wiki/raw/` 目錄中，方便後續由 AI (karpathy-llm-wiki) 進行知識萃取與攝取。

**使用方式**：
在專案根目錄下，使用虛擬環境的 Python 執行：
```powershell
# 自動依網址或網域產生 Markdown 檔名
.venv\Scripts\python.exe scripts\web_to_md.py "https://example.com/article"

# 指定輸出的檔案名稱 (例如：存成 wiki/raw/my_article.md)
.venv\Scripts\python.exe scripts\web_to_md.py "https://example.com/article" -o "my_article"
```

### 2. 備份知識庫 (`backup_wiki.ps1`)

**用途**：使用 Windows 內建的高效 `robocopy` 工具，將本地端的 `wiki/` 目錄完整鏡像備份到 Google Drive 雲端硬碟 (`H:\我的雲端硬碟\DriveSyncFiles\wiki_book`)。同步過程會自動排除 `.git` 目錄並刪除雲端多餘的檔案，確保兩邊完全一致。

**使用方式**：
在 PowerShell 中執行以下指令：
```powershell
.\scripts\backup_wiki.ps1
```
*(注意：執行前請確認 Google Drive 電腦版已掛載，且 `H:` 磁碟機與備份路徑存在)*