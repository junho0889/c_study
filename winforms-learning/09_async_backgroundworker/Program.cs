// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 09 - 비동기 작업과 BackgroundWorker          ■
// ■  파일 다운로더 시뮬레이션 만들기                        ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) BackgroundWorker    - 무거운 작업을 뒤에서 처리 (요리사가 주방에서 요리)
//   2) async/await         - 기다리되 멈추지 않는 방법 (택배 기다리면서 다른 일)
//   3) 진행률 보고         - 작업이 얼마나 됐는지 알려주기 (로딩 바)
//   4) UI 스레드 안전      - 화면 업데이트는 꼭 UI 스레드에서 (교통 규칙)
//   5) Invoke/BeginInvoke  - 다른 스레드에서 UI를 안전하게 변경
//
// ★ 핵심 개념: UI 스레드란? ★
// 화면(버튼, 라벨 등)을 그리고 관리하는 "전담 직원"이 UI 스레드입니다.
// 이 직원이 무거운 작업(파일 다운로드, 계산)까지 하면
// 화면이 멈추고(Not Responding) 사용자가 답답해합니다.
// 그래서 무거운 작업은 "보조 직원(백그라운드 스레드)"에게 맡기고,
// UI 스레드는 화면만 관리하게 해야 합니다!

using System;
using System.ComponentModel;
using System.Drawing;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new DownloaderForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  파일 다운로더 시뮬레이션                          │
// └──────────────────────────────────────────────────┘
public sealed class DownloaderForm : Form
{
    // BackgroundWorker 관련
    private readonly BackgroundWorker _worker;
    private readonly ProgressBar _workerProgress;
    private readonly Label _workerStatus;
    private readonly Button _workerStartBtn;
    private readonly Button _workerCancelBtn;

    // async/await 관련
    private readonly ProgressBar _asyncProgress;
    private readonly Label _asyncStatus;
    private readonly Button _asyncStartBtn;
    private readonly Button _asyncCancelBtn;
    private CancellationTokenSource? _cts;

    // Invoke 예제
    private readonly Label _threadLabel;

    public DownloaderForm()
    {
        Text = "파일 다운로더 - 비동기 작업 학습";
        Size = new Size(650, 550);
        StartPosition = FormStartPosition.CenterScreen;

        var mainPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 1,
            RowCount = 3,
            Padding = new Padding(15)
        };
        mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 40));
        mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 40));
        mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 20));

        // ┌──────────────────────────────────────────┐
        // │  1부: BackgroundWorker 방식               │
        // └──────────────────────────────────────────┘
        // BackgroundWorker는 "요리사 + 주방" 시스템입니다.
        //   - DoWork         → 주방에서 요리 (백그라운드 스레드)
        //   - ProgressChanged → "지금 70% 됐어요!" (진행률 보고)
        //   - RunWorkerCompleted → "요리 완성!" (작업 완료 알림)
        //
        // DoWork에서는 절대로 UI를 직접 건드리면 안 됩니다!
        // 요리사가 주방에서 직접 손님 테이블을 치우면 안 되는 것처럼,
        // ProgressChanged를 통해 "웨이터(UI 스레드)"에게 부탁해야 합니다.

        var workerGroup = new GroupBox
        {
            Text = "1. BackgroundWorker 방식",
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11, FontStyle.Bold),
            Padding = new Padding(10)
        };

        var workerPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 3
        };
        workerPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 70));
        workerPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 30));

        _workerProgress = new ProgressBar
        {
            Dock = DockStyle.Fill,
            Style = ProgressBarStyle.Continuous,
            Minimum = 0,
            Maximum = 100
        };
        workerPanel.Controls.Add(_workerProgress, 0, 0);

        var workerBtnPanel = new FlowLayoutPanel { Dock = DockStyle.Fill };
        _workerStartBtn = new Button { Text = "시작", Width = 60 };
        _workerStartBtn.Click += WorkerStart_Click;
        _workerCancelBtn = new Button { Text = "취소", Width = 60, Enabled = false };
        _workerCancelBtn.Click += (s, e) => _worker.CancelAsync();
        workerBtnPanel.Controls.Add(_workerStartBtn);
        workerBtnPanel.Controls.Add(_workerCancelBtn);
        workerPanel.Controls.Add(workerBtnPanel, 1, 0);

        _workerStatus = new Label
        {
            Text = "BackgroundWorker: 대기 중...",
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 9, FontStyle.Regular),
            TextAlign = ContentAlignment.MiddleLeft
        };
        workerPanel.Controls.Add(_workerStatus, 0, 1);
        workerPanel.SetColumnSpan(_workerStatus, 2);

        workerGroup.Controls.Add(workerPanel);
        mainPanel.Controls.Add(workerGroup, 0, 0);

        // ── BackgroundWorker 설정 ──
        _worker = new BackgroundWorker
        {
            WorkerReportsProgress = true,      // 진행률 보고 활성화
            WorkerSupportsCancellation = true   // 취소 지원 활성화
        };

        // DoWork: 백그라운드에서 실행되는 코드
        _worker.DoWork += Worker_DoWork;
        // ProgressChanged: 진행률이 바뀔 때 (UI 스레드에서 실행)
        _worker.ProgressChanged += Worker_ProgressChanged;
        // RunWorkerCompleted: 작업이 끝났을 때 (UI 스레드에서 실행)
        _worker.RunWorkerCompleted += Worker_Completed;

        // ┌──────────────────────────────────────────┐
        // │  2부: async/await 방식 (현대적 방법)       │
        // └──────────────────────────────────────────┘
        // async/await는 "택배를 기다리면서 다른 일하기"입니다.
        //   await = "이 작업이 끝날 때까지 기다릴게, 그동안 다른 일 해도 돼"
        //   async = "이 메서드는 await를 쓸 수 있어요"라는 표시
        //
        // BackgroundWorker보다 코드가 훨씬 간결하고 읽기 쉽습니다!

        var asyncGroup = new GroupBox
        {
            Text = "2. async/await 방식 (권장)",
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11, FontStyle.Bold),
            Padding = new Padding(10)
        };

        var asyncPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 2
        };
        asyncPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 70));
        asyncPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 30));

        _asyncProgress = new ProgressBar
        {
            Dock = DockStyle.Fill,
            Style = ProgressBarStyle.Continuous,
            Minimum = 0,
            Maximum = 100
        };
        asyncPanel.Controls.Add(_asyncProgress, 0, 0);

        var asyncBtnPanel = new FlowLayoutPanel { Dock = DockStyle.Fill };
        _asyncStartBtn = new Button { Text = "시작", Width = 60 };
        _asyncStartBtn.Click += AsyncStart_Click;
        _asyncCancelBtn = new Button { Text = "취소", Width = 60, Enabled = false };
        _asyncCancelBtn.Click += (s, e) => _cts?.Cancel();
        asyncBtnPanel.Controls.Add(_asyncStartBtn);
        asyncBtnPanel.Controls.Add(_asyncCancelBtn);
        asyncPanel.Controls.Add(asyncBtnPanel, 1, 0);

        _asyncStatus = new Label
        {
            Text = "async/await: 대기 중...",
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 9, FontStyle.Regular),
            TextAlign = ContentAlignment.MiddleLeft
        };
        asyncPanel.Controls.Add(_asyncStatus, 0, 1);
        asyncPanel.SetColumnSpan(_asyncStatus, 2);

        asyncGroup.Controls.Add(asyncPanel);
        mainPanel.Controls.Add(asyncGroup, 0, 1);

        // ┌──────────────────────────────────────────┐
        // │  3부: Invoke 예제                         │
        // └──────────────────────────────────────────┘
        // Invoke는 "다른 스레드에서 UI 스레드에게 부탁하기"입니다.
        // 교실에서 다른 반 학생이 우리 반 선생님께 전달할 말이 있으면,
        // 직접 칠판에 쓰지 않고 우리 반 선생님께 "대신 써주세요" 부탁하는 것!
        var invokeGroup = new GroupBox
        {
            Text = "3. Invoke/BeginInvoke 예제",
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11, FontStyle.Bold),
            Padding = new Padding(10)
        };

        var invokePanel = new FlowLayoutPanel { Dock = DockStyle.Fill };

        var invokeBtn = new Button { Text = "스레드에서 UI 업데이트", Width = 180 };
        invokeBtn.Click += InvokeExample_Click;
        invokePanel.Controls.Add(invokeBtn);

        _threadLabel = new Label
        {
            Text = "아직 업데이트되지 않음",
            AutoSize = true,
            Font = new Font("맑은 고딕", 10, FontStyle.Regular),
            Margin = new Padding(10, 5, 0, 0)
        };
        invokePanel.Controls.Add(_threadLabel);

        invokeGroup.Controls.Add(invokePanel);
        mainPanel.Controls.Add(invokeGroup, 0, 2);

        Controls.Add(mainPanel);
    }

    // ┌──────────────────────────────────────────┐
    // │  BackgroundWorker - DoWork               │
    // │  (백그라운드 스레드에서 실행)              │
    // └──────────────────────────────────────────┘
    private void Worker_DoWork(object? sender, DoWorkEventArgs e)
    {
        // 이 메서드는 별도의 스레드에서 실행됩니다.
        // 여기서 UI 컨트롤을 직접 건드리면 오류가 발생합니다!
        // ReportProgress로 진행률만 보고합니다.

        for (int i = 0; i <= 100; i++)
        {
            if (_worker.CancellationPending) // 취소 요청 확인
            {
                e.Cancel = true;
                return;
            }

            Thread.Sleep(50); // 다운로드 시뮬레이션 (50ms 대기)
            _worker.ReportProgress(i, $"다운로드 중... {i}% (파일 {i}/100)");
        }
    }

    private void Worker_ProgressChanged(object? sender, ProgressChangedEventArgs e)
    {
        // 이 메서드는 UI 스레드에서 실행됩니다.
        // 안전하게 컨트롤을 업데이트할 수 있습니다!
        _workerProgress.Value = e.ProgressPercentage;
        _workerStatus.Text = e.UserState?.ToString() ?? "";
    }

    private void Worker_Completed(object? sender, RunWorkerCompletedEventArgs e)
    {
        _workerStartBtn.Enabled = true;
        _workerCancelBtn.Enabled = false;

        if (e.Cancelled)
            _workerStatus.Text = "BackgroundWorker: 취소됨!";
        else if (e.Error != null)
            _workerStatus.Text = $"BackgroundWorker: 오류 - {e.Error.Message}";
        else
            _workerStatus.Text = "BackgroundWorker: 다운로드 완료!";
    }

    private void WorkerStart_Click(object? sender, EventArgs e)
    {
        _workerProgress.Value = 0;
        _workerStartBtn.Enabled = false;
        _workerCancelBtn.Enabled = true;
        _worker.RunWorkerAsync(); // 백그라운드 작업 시작!
    }

    // ┌──────────────────────────────────────────┐
    // │  async/await 방식                         │
    // └──────────────────────────────────────────┘
    // async 메서드는 await를 만나면 잠시 멈추고,
    // UI 스레드가 다른 일(버튼 클릭, 화면 그리기)을 할 수 있게 합니다.
    // await가 끝나면 다시 돌아와서 다음 코드를 실행합니다.
    private async void AsyncStart_Click(object? sender, EventArgs e)
    {
        _asyncProgress.Value = 0;
        _asyncStartBtn.Enabled = false;
        _asyncCancelBtn.Enabled = true;
        _cts = new CancellationTokenSource();

        try
        {
            // Progress<T>는 진행률을 UI 스레드에서 보고하는 도구입니다.
            var progress = new Progress<int>(percent =>
            {
                // 이 콜백은 UI 스레드에서 실행됩니다!
                _asyncProgress.Value = percent;
                _asyncStatus.Text = $"async 다운로드 중... {percent}%";
            });

            // await로 무거운 작업을 기다리되, UI는 멈추지 않습니다.
            await SimulateDownloadAsync(progress, _cts.Token);

            _asyncStatus.Text = "async/await: 다운로드 완료!";
        }
        catch (OperationCanceledException)
        {
            _asyncStatus.Text = "async/await: 취소됨!";
        }
        finally
        {
            _asyncStartBtn.Enabled = true;
            _asyncCancelBtn.Enabled = false;
            _cts.Dispose();
        }
    }

    // Task.Run으로 무거운 작업을 백그라운드 스레드에서 실행합니다.
    private async Task SimulateDownloadAsync(IProgress<int> progress, CancellationToken token)
    {
        await Task.Run(() =>
        {
            for (int i = 0; i <= 100; i++)
            {
                token.ThrowIfCancellationRequested(); // 취소 요청 시 예외 발생
                Thread.Sleep(40);
                progress.Report(i); // 진행률 보고
            }
        }, token);
    }

    // ┌──────────────────────────────────────────┐
    // │  Invoke/BeginInvoke 예제                  │
    // └──────────────────────────────────────────┘
    private void InvokeExample_Click(object? sender, EventArgs e)
    {
        // 새 스레드를 만들어서 UI 업데이트를 시도합니다.
        var thread = new Thread(() =>
        {
            // 잘못된 방법 (주석 처리):
            // _threadLabel.Text = "직접 접근!"; // ← 오류 발생!

            // 올바른 방법: Invoke 사용
            // InvokeRequired는 "지금 UI 스레드인가?"를 확인합니다.
            if (_threadLabel.InvokeRequired)
            {
                // Invoke: UI 스레드에서 실행되도록 "부탁"합니다.
                // 동기(기다림) 방식
                _threadLabel.Invoke(new Action(() =>
                {
                    _threadLabel.Text =
                        $"Invoke로 안전하게 업데이트! " +
                        $"(시간: {DateTime.Now:HH:mm:ss})";
                    _threadLabel.ForeColor = Color.DarkBlue;
                }));

                // BeginInvoke: 비동기(안 기다림) 방식
                // "부탁만 하고 나는 바로 다음 일 할게"
                _threadLabel.BeginInvoke(new Action(() =>
                {
                    _threadLabel.Text += " [BeginInvoke 추가 메시지]";
                }));
            }
        });
        thread.Start();
    }
}
