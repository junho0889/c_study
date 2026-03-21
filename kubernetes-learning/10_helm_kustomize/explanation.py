"""
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■  Kubernetes 학습 10단계: Helm, Kustomize, 배포 전략 개념 설명             ■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

이 파일은 Helm 차트, Kustomize 오버레이, 배포 전략(Blue-Green, Canary)을
설명합니다. 이 주제들은 YAML 파일 하나로는 실습하기 어려워서
개념 설명에 집중합니다.

실행: python explanation.py
"""


def lesson1_why_helm():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 1: 왜 Helm이 필요한가?                     │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 1: 왜 Helm이 필요한가?")
    print("=" * 70)
    print()
    print("  문제: 실제 애플리케이션은 YAML 파일이 수십 개 필요합니다.")
    print("    - Deployment, Service, ConfigMap, Secret, Ingress, HPA...")
    print("    - 개발/스테이징/운영 환경마다 값이 다릅니다.")
    print("    - 같은 앱을 여러 팀이 약간씩 다르게 배포합니다.")
    print()
    print("  Helm은 'Kubernetes의 패키지 관리자'입니다.")
    print("  비유: apt(Ubuntu)나 brew(Mac)처럼,")
    print("        복잡한 앱을 한 번에 설치/업데이트/삭제할 수 있습니다.")
    print()
    print("  Helm 없이:")
    print("    kubectl apply -f deployment.yaml")
    print("    kubectl apply -f service.yaml")
    print("    kubectl apply -f configmap.yaml")
    print("    kubectl apply -f secret.yaml")
    print("    kubectl apply -f ingress.yaml")
    print("    ... (파일마다 환경별 값을 일일이 수정)")
    print()
    print("  Helm 사용:")
    print("    helm install my-app ./my-chart -f values-prod.yaml")
    print("    (한 줄로 모든 리소스를 배포하고, 값만 파일로 바꿀 수 있음!)")
    print()


def lesson2_helm_chart_structure():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 2: Helm 차트 구조                          │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 2: Helm 차트 구조")
    print("=" * 70)
    print()
    print("  Helm 차트는 '레시피 묶음'과 같습니다.")
    print("  폴더 구조:")
    print()
    print("    my-chart/")
    print("    ├── Chart.yaml          # 차트 정보 (이름, 버전, 설명)")
    print("    ├── values.yaml         # 기본 설정값 (재료 목록)")
    print("    ├── templates/          # YAML 템플릿 (조리법)")
    print("    │   ├── deployment.yaml")
    print("    │   ├── service.yaml")
    print("    │   ├── ingress.yaml")
    print("    │   ├── _helpers.tpl    # 공통 함수/변수")
    print("    │   └── NOTES.txt       # 설치 후 안내 메시지")
    print("    └── charts/             # 의존하는 다른 차트")
    print()
    print("  [Chart.yaml] - 차트의 신분증")
    print("  ─────────────────────────────")
    print("    apiVersion: v2")
    print("    name: my-app")
    print("    version: 1.0.0           # 차트 자체의 버전")
    print("    appVersion: '2.1.0'      # 배포하는 앱의 버전")
    print("    description: 나의 웹 애플리케이션")
    print()
    print("  [values.yaml] - 기본 설정값")
    print("  ─────────────────────────────")
    print("    replicaCount: 2")
    print("    image:")
    print("      repository: nginx")
    print("      tag: '1.27'")
    print("    service:")
    print("      type: ClusterIP")
    print("      port: 80")
    print()
    print("  [templates/deployment.yaml] - 템플릿 (Go 템플릿 문법)")
    print("  ────────────────────────────────────────────────────")
    print("    replicas: {{ .Values.replicaCount }}")
    print("    image: {{ .Values.image.repository }}:{{ .Values.image.tag }}")
    print()
    print("  비유: values.yaml은 '주문서'이고, templates는 '조리법'입니다.")
    print("        주문서의 재료를 바꾸면 같은 조리법으로 다른 음식이 나옵니다.")
    print()


def lesson3_helm_commands():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 3: Helm 주요 명령어                        │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 3: Helm 주요 명령어")
    print("=" * 70)
    print()
    print("  [설치]")
    print("  helm install <릴리스이름> <차트경로>")
    print("  helm install my-app ./my-chart")
    print("  helm install my-app ./my-chart -f values-prod.yaml   # 환경별 값")
    print("  helm install my-app ./my-chart --set replicaCount=5  # 값 직접 지정")
    print()
    print("  [업그레이드]")
    print("  helm upgrade my-app ./my-chart")
    print("  helm upgrade my-app ./my-chart -f values-prod.yaml")
    print()
    print("  [롤백]")
    print("  helm rollback my-app 1            # 리비전 1로 롤백")
    print("  helm history my-app               # 리비전 이력 확인")
    print()
    print("  [삭제]")
    print("  helm uninstall my-app")
    print()
    print("  [차트 레포지토리]")
    print("  helm repo add bitnami https://charts.bitnami.com/bitnami")
    print("  helm search repo nginx            # 차트 검색")
    print("  helm pull bitnami/nginx           # 차트 다운로드")
    print()
    print("  [디버그]")
    print("  helm template my-app ./my-chart   # 렌더링 결과만 확인 (적용 안 함)")
    print("  helm lint ./my-chart              # 차트 문법 검사")
    print("  helm install my-app ./my-chart --dry-run  # 시뮬레이션")
    print()


def lesson4_kustomize():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 4: Kustomize (템플릿 없는 커스터마이징)     │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 4: Kustomize (템플릿 없는 커스터마이징)")
    print("=" * 70)
    print()
    print("  Kustomize는 Helm과 다른 접근 방식입니다.")
    print("  '원본 YAML을 수정하지 않고, 위에 덮어쓰기(overlay)'하는 방식입니다.")
    print()
    print("  비유:")
    print("    Helm       = 레시피를 처음부터 템플릿으로 작성")
    print("    Kustomize  = 기본 레시피 위에 포스트잇으로 수정사항 붙이기")
    print()
    print("  폴더 구조:")
    print("    my-app/")
    print("    ├── base/                    # 기본 YAML (공통)")
    print("    │   ├── kustomization.yaml")
    print("    │   ├── deployment.yaml")
    print("    │   └── service.yaml")
    print("    └── overlays/                # 환경별 수정사항")
    print("        ├── dev/")
    print("        │   ├── kustomization.yaml")
    print("        │   └── replica-patch.yaml")
    print("        └── prod/")
    print("            ├── kustomization.yaml")
    print("            └── replica-patch.yaml")
    print()
    print("  [base/kustomization.yaml]")
    print("  ─────────────────────────")
    print("    resources:")
    print("      - deployment.yaml")
    print("      - service.yaml")
    print()
    print("  [overlays/prod/kustomization.yaml]")
    print("  ────────────────────────────────────")
    print("    resources:")
    print("      - ../../base")
    print("    patches:")
    print("      - replica-patch.yaml")
    print("    namespace: production")
    print("    namePrefix: prod-")
    print()
    print("  사용법:")
    print("    kubectl apply -k overlays/dev/    # dev 환경 적용")
    print("    kubectl apply -k overlays/prod/   # prod 환경 적용")
    print()
    print("  장점: kubectl에 내장되어 있어서 별도 설치가 필요 없습니다!")
    print()


def lesson5_helm_vs_kustomize():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 5: Helm vs Kustomize 비교                  │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 5: Helm vs Kustomize 비교")
    print("=" * 70)
    print()
    print("  ┌──────────────────┬─────────────────────┬──────────────────────┐")
    print("  │                  │ Helm                │ Kustomize            │")
    print("  ├──────────────────┼─────────────────────┼──────────────────────┤")
    print("  │ 접근 방식        │ 템플릿 엔진         │ 오버레이(덮어쓰기)   │")
    print("  │ 학습 곡선        │ 높음 (Go 템플릿)    │ 낮음 (순수 YAML)     │")
    print("  │ 패키지 공유      │ 차트 레포지토리     │ Git 레포지토리       │")
    print("  │ 버전 관리        │ 릴리스+롤백         │ Git으로 관리         │")
    print("  │ 설치 필요        │ helm CLI 필요       │ kubectl에 내장       │")
    print("  │ 커뮤니티 차트    │ 풍부함              │ 없음                 │")
    print("  │ 적합한 경우      │ 복잡한 앱, 공유     │ 간단한 환경별 차이   │")
    print("  └──────────────────┴─────────────────────┴──────────────────────┘")
    print()
    print("  실전 조언:")
    print("    - 외부 오픈소스 앱 설치 → Helm (Prometheus, Grafana 등)")
    print("    - 자체 앱의 환경별 배포 → Kustomize 또는 Helm 둘 다 가능")
    print("    - 팀이 작고 간단한 경우 → Kustomize 추천")
    print("    - 팀이 크고 복잡한 경우 → Helm 추천")
    print("    - 둘을 함께 사용하는 것도 가능합니다!")
    print()


def lesson6_blue_green_deployment():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 6: Blue-Green 배포                         │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 6: Blue-Green 배포")
    print("=" * 70)
    print()
    print("  Blue-Green 배포는 '두 개의 동일한 환경'을 운영하는 방식입니다.")
    print()
    print("  비유: 무대에서 장면 전환할 때")
    print("    - Blue 무대 (현재 버전): 관객에게 보이는 중")
    print("    - Green 무대 (새 버전): 뒤에서 준비 중")
    print("    - 준비 완료되면 → 조명을 Green으로 전환! (즉시 전환)")
    print("    - 문제 발생 시 → 조명을 Blue로 다시 전환! (즉시 롤백)")
    print()
    print("  동작 흐름:")
    print("    1. Blue(v1)가 운영 중")
    print("    2. Green(v2)를 별도로 배포하고 테스트")
    print("    3. Service의 selector를 Green으로 전환")
    print("    4. 문제 있으면 selector를 Blue로 되돌림")
    print()
    print("  Kubernetes에서 구현:")
    print("    # Blue Deployment (app=myapp, version=blue)")
    print("    # Green Deployment (app=myapp, version=green)")
    print("    # Service selector를 version: blue → version: green 으로 변경")
    print()
    print("  장점: 즉시 전환, 즉시 롤백 가능")
    print("  단점: 리소스가 2배 필요 (두 환경을 동시에 운영)")
    print()


def lesson7_canary_deployment():
    """
    ┌─────────────────────────────────────────────────┐
    │  레슨 7: Canary 배포                             │
    └─────────────────────────────────────────────────┘
    """
    print("=" * 70)
    print("  레슨 7: Canary 배포")
    print("=" * 70)
    print()
    print("  Canary 배포는 '새 버전을 소수의 사용자에게 먼저 공개'하는 방식입니다.")
    print()
    print("  이름의 유래: 탄광에서 카나리아 새를 먼저 보내서 안전한지 확인한 것")
    print("               새가 괜찮으면 광부들이 들어갑니다.")
    print()
    print("  동작 흐름:")
    print("    1. v1이 9개 Pod로 운영 중")
    print("    2. v2를 1개 Pod만 추가 (전체의 10%)")
    print("    3. v2의 에러율, 응답 시간 등을 모니터링")
    print("    4. 정상이면 v2를 점진적으로 늘림 (10% → 30% → 50% → 100%)")
    print("    5. 문제 있으면 v2를 즉시 0개로 줄임")
    print()
    print("  비유: 신메뉴 출시")
    print("    - 전체 매장 중 1개 매장에서만 먼저 판매")
    print("    - 반응이 좋으면 점차 모든 매장으로 확대")
    print("    - 반응이 나쁘면 해당 매장에서만 중단")
    print()
    print("  Kubernetes에서 구현:")
    print("    # v1 Deployment: replicas: 9")
    print("    # v2 Deployment: replicas: 1")
    print("    # 같은 Service selector로 두 Deployment의 트래픽을 합침")
    print("    # 점진적으로 v2 replicas 증가, v1 replicas 감소")
    print()
    print("  고급 도구: Istio, Argo Rollouts → 트래픽 비율을 정밀 제어 가능")
    print("    예: '5%만 v2로 보내기' → HTTP 헤더/쿠키 기반 분배")
    print()
    print("  ┌──────────────┬──────────────────┬──────────────────┐")
    print("  │              │ Blue-Green       │ Canary           │")
    print("  ├──────────────┼──────────────────┼──────────────────┤")
    print("  │ 전환 방식    │ 한 번에 전부     │ 점진적 확대      │")
    print("  │ 리소스 필요  │ 2배              │ 조금만 추가      │")
    print("  │ 위험도       │ 낮음 (즉시 롤백) │ 매우 낮음        │")
    print("  │ 피드백       │ 전환 후에만      │ 실시간 모니터링  │")
    print("  │ 복잡도       │ 단순             │ 복잡             │")
    print("  └──────────────┴──────────────────┴──────────────────┘")
    print()


if __name__ == "__main__":
    lesson1_why_helm()
    lesson2_helm_chart_structure()
    lesson3_helm_commands()
    lesson4_kustomize()
    lesson5_helm_vs_kustomize()
    lesson6_blue_green_deployment()
    lesson7_canary_deployment()
