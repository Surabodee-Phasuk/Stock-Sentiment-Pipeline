#!/usr/bin/env bash
# ตรวจว่า credential ในเครื่องเข้าถึง resource ของ INFRA-02 ได้ (ไม่สร้าง/ลบอะไร ยกเว้นไฟล์ผลลัพธ์ของ Athena)
# ใช้: bash infra/aws/check.sh   (เลือก profile ด้วย AWS_PROFILE=...)
set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-2}"
BUCKET="${BUCKET:-stock-sentiment-lakehouse-surabodee}"
GLUE_DB="${GLUE_DB:-stock_sentiment}"
WORKGROUP="${WORKGROUP:-stock-sentiment}"

step() { printf '\n== %s\n' "$1"; }

step "identity"
aws sts get-caller-identity --query '[Account,Arn]' --output text

step "s3: list s3://$BUCKET"
aws s3 ls "s3://$BUCKET/" --region "$REGION"

step "glue: database $GLUE_DB"
aws glue get-database --name "$GLUE_DB" --region "$REGION" --query 'Database.Name' --output text

step "athena: workgroup $WORKGROUP result location"
aws athena get-work-group --work-group "$WORKGROUP" --region "$REGION" \
  --query 'WorkGroup.Configuration.ResultConfiguration.OutputLocation' --output text

step "athena: SELECT 1"
qid=$(aws athena start-query-execution --work-group "$WORKGROUP" --region "$REGION" \
  --query-string 'SELECT 1' --query QueryExecutionId --output text)
for _ in $(seq 1 30); do
  state=$(aws athena get-query-execution --query-execution-id "$qid" --region "$REGION" \
    --query QueryExecution.Status.State --output text)
  case "$state" in
    SUCCEEDED) break ;;
    FAILED | CANCELLED)
      aws athena get-query-execution --query-execution-id "$qid" --region "$REGION" \
        --query QueryExecution.Status.StateChangeReason --output text
      exit 1 ;;
  esac
  sleep 1
done
[ "$state" = SUCCEEDED ] || { echo "timeout: $state"; exit 1; }
aws athena get-query-results --query-execution-id "$qid" --region "$REGION" \
  --query 'ResultSet.Rows[1].Data[0].VarCharValue' --output text

printf '\nall checks passed\n'
