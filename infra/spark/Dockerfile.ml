# F3-01: Spark image เดิม + torch (CPU) + transformers สำหรับรัน FinBERT บน driver
# build ครั้งแรกใช้เวลาหลายนาที (torch CPU ~200 MB) หลังจากนั้นใช้ cache
FROM apache/spark:4.0.4-scala2.13-java17-python3-ubuntu

USER root
RUN python3 -m pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu "torch==2.5.1" \
    && python3 -m pip install --no-cache-dir "transformers>=4.44,<5"

# cache ของโมเดลจาก Hugging Face (mount เป็น volume ให้โหลดแค่ครั้งแรก)
ENV HF_HOME=/opt/hf-cache
