`macro_df` là tầng dữ liệu sâu nhất, đại diện cho **"Sức khỏe nội tại"** của một nền kinh tế. Trong khi [indexes_df](cci:1://file:///home/duongvct/Documents/workspace/PTIT/Y4T2/FX_BOT/04.deployment_automation/scripts/transform.py:577:2-602:15) là tâm lý thị trường, `macro_df` chính là nền tảng cốt lõi quyết định giá trị đồng tiền trong dài hạn.

Dưới đây là phân tích chi tiết:

### 1. Chi tiết cách lấy và biến đổi ban đầu (Logic)

Tác giả lấy dữ liệu từ **FRED** (Kho dữ liệu của Ngân hàng Dự trữ Liên bang Mỹ) với các thành phần:
*   **GDP (Quý):** Tổng sản phẩm quốc nội - Đo lường sức mạnh kinh tế.
*   **CPI Core (Tháng):** Chỉ số giá tiêu dùng - Đo lường lạm phát (loại bỏ thực phẩm & năng lượng).
*   **Trade Balance (Tháng):** Cán cân thương mại - Sự chênh lệch giữa xuất khẩu và nhập khẩu.
*   **FEDFUNDS (Tháng):** Lãi suất liên bang - Công cụ quyền lực nhất của FED để điều khiển dòng tiền.
*   **Bond Yields (Hàng ngày):** Lợi suất trái phiếu chính phủ Mỹ kỳ hạn 1 năm (`DGS1`), 5 năm (`DGS5`), và 10 năm (`DGS10`).

**Biến đổi kỹ thuật đặc biệt (Merging & Resampling):**
Vì dữ liệu Macro có tần suất rất khác nhau (Quý, Tháng, Ngày), tác giả đã thực hiện một kỹ thuật rất thông minh:
1.  **Chuyển đổi sang tỷ lệ:** Tính toán **YoY** (So với cùng kỳ năm ngoái) và **QoQ/MoM** (So với kỳ trước) cho GDP, CPI, Trade Balance.
2.  **Đưa về dữ liệu ngày:** Tác giả dùng lệnh `dt.to_period` để gán nhãn thời gian thống nhất.
3.  **Forward Fill (`ffill()`):** Vì GDP chỉ có 4 lần/năm, tác giả "kéo dài" giá trị đó cho tất cả các ngày trong quý. Kết quả là tạo ra một bảng dữ liệu liên tục hằng ngày cho các biến số vĩ mô.

### 2. Tại sao tác giả lại làm như thế? (Chiến thuật)

*   **Lãi suất là "Vua" (Interest Rate Parity):** Trong Forex, dòng tiền luôn chảy về nơi có lãi suất cao hơn. Bằng cách lấy `FEDFUNDS` và `Bond Yields`, tác giả giúp AI hiểu được lực hút của đồng USD.
*   **Nắm bắt Đường cong lợi suất (Yield Curve):** Việc lấy cả kỳ hạn 1 năm, 5 năm và 10 năm giúp AI nhận diện được hiện tượng **"Đường cong lợi suất nghịch đảo"** (Báo hiệu suy thoái). Đây là tín hiệu cực mạnh để các tổ chức tài chính lớn rút vốn khỏi các tài sản rủi ro.
*   **Hiểu được "Động lực" lạm phát:** Tỷ lệ **YoY** của CPI giúp AI biết lạm phát đang tăng tốc hay giảm tốc. Nếu lạm phát tăng, AI sẽ dự đoán FED sắp tăng lãi suất -> Đồng USD sẽ mạnh lên.

### 3. Ảnh hưởng của nó đến chiến lược và mô hình

*   **Điểm tựa cho xu hướng dài hạn:** Các chỉ báo kỹ thuật (RSI, MACD) có thể báo "Quá mua", nhưng nếu GDP đang tăng trưởng cực tốt và lãi suất cao, đồng tiền đó vẫn có thể tiếp tục tăng. `macro_df` giúp AI không đi ngược lại xu hướng lớn của nền kinh tế.
*   **Định vị tính chất của tài sản:** Nhờ `macro_df`, AI có thể phân biệt được bối cảnh:
    - **Môi trường tăng trưởng:** Ủng hộ các cặp tiền như AUD, NZD.
    - **Môi trường suy thoái:** Ủng hộ các cặp tiền "trú ẩn" như USD, JPY.
*   **Tạo ra sự khác biệt với Trading bot thông thường:** Đa số các bot trên thị trường chỉ nhìn vào biểu đồ nến (Technical). Bot của tác giả nhìn vào cả "Nguyên nhân gốc rễ" (Fundamental). Điều này giúp giảm thiểu rủi ro khi có các tin tức kinh tế lớn cực mạnh được công bố.

**Tóm lại:** `macro_df` biến dữ liệu Forex khô khan thành một câu chuyện kinh tế có tính logic. Nó cung cấp chiếc **"Neo"** để mô hình AI không bị rung lắc quá mạnh bởi các biến động ảo trong ngắn hạn.