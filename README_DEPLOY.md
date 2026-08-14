# Skincare Analytics — Dashboard & Hướng dẫn deploy

## Có gì mới trong bản này (dành cho người xem: giám đốc & khách hàng)

Toàn bộ 6 dashboard đã được bổ sung phần chú thích để người không chuyên về dữ liệu vẫn đọc hiểu được:

| Bổ sung | Mô tả |
|---|---|
| **Thanh “Đang xem”** | Ngay dưới thanh điều hướng, hiển thị đúng khoảng thời gian + các bộ lọc đang áp dụng + số dòng giao dịch. Tránh hiểu nhầm khi trình bày. |
| **Ô “Đọc nhanh” (viền vàng)** | Dưới mỗi biểu đồ là một câu kết luận **tự động tính từ chính dữ liệu đang lọc** — ví dụ *“Serum dẫn đầu với 18,52 tỷ (28,6% doanh thu), gấp 1,4 lần Sunscreen”*. Đổi bộ lọc thì câu này đổi theo. |
| **Ô “Cách đọc biểu đồ này & chi tiết kỹ thuật”** | Expander gập lại dưới mỗi biểu đồ: phần **Đọc thế nào** viết bằng ngôn ngữ đời thường cho giám đốc; phần **Chi tiết kỹ thuật** ghi rõ công thức, bảng nguồn, tham số mô hình cho hội đồng chấm. |
| **Tooltip (i) trên tiêu đề biểu đồ** | Di chuột vào biểu tượng tròn cạnh tên biểu đồ để xem giải thích ngắn mà không cần rời màn hình. |
| **Bảng giải nghĩa chỉ số** | Dưới mỗi hàng KPI có một dải giải nghĩa từng chỉ số bằng tiếng Việt kèm công thức (AOV, Repeat Rate, Cohort, CLV, ROC-AUC…). |
| **Nút “Tải dữ liệu biểu đồ (.csv)”** | Mỗi biểu đồ cho tải đúng bảng số liệu đứng sau nó, để đưa vào Excel/Word hoặc kiểm chứng con số. |
| **Nhãn trục & hover tiếng Việt** | Mọi trục đều có tên và đơn vị; hover hiện đúng định dạng (VNĐ, %, số đơn). |

### Hai công tắc ở thanh bên trái

- **Giải thích chi tiết** — BẬT (mặc định): hiện đầy đủ ô “Cách đọc & chi tiết kỹ thuật”, phù hợp khi trình bày cho người xem lần đầu. TẮT: giao diện gọn, chỉ còn biểu đồ + câu Đọc nhanh.
- **Nút tải dữ liệu (.csv)** — bật/tắt các nút tải để màn hình đỡ rối khi chiếu slide.

> Gợi ý khi thuyết trình: bật cả hai công tắc, đi lần lượt 6 tab từ trái sang phải. Mỗi biểu đồ chỉ cần đọc to câu trong ô vàng “Đọc nhanh” là đã có kết luận.

### Một đính chính quan trọng về trang 5 (Phát hiện Bất thường)

Ngưỡng IQR trong `mart_anomaly_flag` được tính **riêng cho từng mã sản phẩm**, không phải một ngưỡng chung cho toàn shop, và cờ bất thường gồm **cả hai chiều**: cao bất thường (vượt Q3 + 1,5×IQR, ~81% số ca) và thấp bất thường (dưới Q1 − 1,5×IQR, ~19%). Phần chú thích trên trang đã được viết lại cho đúng với cách dữ liệu thực sự được gắn cờ.

---

# Deploy lên Streamlit Community Cloud (miễn phí)

## Cấu trúc thư mục (đã sắp sẵn trong file zip này)
```
app.py
requirements.txt
DW_SCHEMA_VI/
    dim_brand.csv
    dim_category.csv
    dim_channel.csv
    dim_customer.csv
    dim_date.csv
    dim_geography.csv
    dim_payment.csv
    dim_product.csv
    dim_shop.csv
    fact_product_snapshot.csv
    fact_transaction.csv
    mart_anomaly_flag.csv
    mart_cohort_retention.csv
    mart_customer_rfm.csv
```
`app.py` tự tìm dữ liệu trong thư mục `DW_SCHEMA_VI` nằm cạnh nó, nên giữ nguyên cấu trúc này khi đưa lên GitHub.

## Các bước deploy

1. **Tạo repo GitHub** (public hoặc private đều được):
   - Vào github.com > New repository > đặt tên (vd: `skincare-dashboard`) > Create.

2. **Đưa toàn bộ nội dung thư mục này lên repo**:
   - Cách nhanh nhất: vào repo trên GitHub > "Add file" > "Upload files" > kéo thả toàn bộ `app.py`, `requirements.txt`, và cả thư mục `DW_SCHEMA_VI` (kéo cả folder) > Commit.
   - Hoặc dùng Git CLI:
     ```
     git init
     git add .
     git commit -m "Initial commit"
     git branch -M main
     git remote add origin https://github.com/<username>/<repo>.git
     git push -u origin main
     ```

3. **Deploy trên Streamlit Community Cloud**:
   - Vào https://share.streamlit.io > đăng nhập bằng tài khoản GitHub.
   - Bấm "New app" > chọn repo vừa tạo > branch `main` > Main file path: `app.py` > Deploy.
   - Đợi 2-5 phút để build xong (cài các thư viện trong requirements.txt).

4. Sau khi build xong, bạn sẽ có link công khai dạng:
   `https://<tenapp>-<random>.streamlit.app`
   Gửi link này cho bất kỳ ai để họ xem dashboard trên trình duyệt, không cần cài đặt gì.

## Lưu ý

- App có dùng thư viện `prophet` và `lifetimes` cho phần Dự báo/CLV, nhưng code đã tự viết fallback (dùng OLS/heuristic) nếu không có 2 thư viện này — nên **không cần** thêm chúng vào requirements.txt để tránh lỗi build (2 thư viện này khá nặng và đôi khi khó cài trên môi trường cloud miễn phí). Nếu muốn dùng đúng Prophet/lifetimes, có thể thêm `prophet` và `lifetimes` vào requirements.txt, nhưng thời gian build sẽ lâu hơn.
- Ứng dụng free tier của Streamlit Cloud giới hạn khoảng 1GB RAM — với dữ liệu ~28MB CSV như hiện tại là hoàn toàn ổn.
- Nếu sau này cập nhật dữ liệu/code, chỉ cần push lên GitHub, app sẽ tự động build lại.
