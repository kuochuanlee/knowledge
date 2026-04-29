---
title: "{真實人類易讀標題，若無則從內容摘要}"
original_filename: "{保留原始檔案名稱，例如：Attention-Is-All-You-Need.md}"
source_url: "{URL 或來源描述，若為本地檔案可填 Local}"
date_collected: "{YYYY-MM-DD}"
date_published: "{YYYY-MM-DD 或是 Unknown}"
tags: 
  - raw
  - {根據內容自動生成的 1~2 個領域標籤}
status: "ingested"
---

# {真實人類易讀標題}

{以下為原始內容。請忠實保留原始文字。清除格式噪音（如多餘空白、破損的 HTML 標籤、網頁導覽列），但絕對不可改寫觀點、不可總結內容、不可改變原意。}

---

## PDF Sidecar 格式範例

當來源為 `.pdf` 時，建立同名 `.md` 代理檔，格式如下：

```markdown
---
title: "{真實人類易讀標題}"
original_filename: "{原始PDF檔名，例如：attention.pdf}"
source_url: "{URL 或來源描述，若為本地檔案可填 Local}"
source_type: "pdf"
date_collected: "{YYYY-MM-DD}"
date_published: "{YYYY-MM-DD 或是 Unknown}"
tags:
  - raw
  - {根據內容自動生成的 1~2 個領域標籤}
status: "ingested"
---

# {真實人類易讀標題}

![[{原始PDF檔名.pdf}]]

{以下為 PDF 純文字萃取內容。忠實轉錄，不可總結或改寫。}
```