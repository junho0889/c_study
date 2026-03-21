using System;
using System.Collections.Generic;

namespace ArchitectureLearning.ObserverPattern
{
    /*
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
      옵저버 패턴 (Observer Pattern)
      실행 방법: dotnet script example.cs  또는  csc example.cs && example.exe
    ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

      옵저버 패턴이란?
      "무슨 일이 생기면 알려줘!"라고 등록해 두면,
      일이 생겼을 때 자동으로 알림을 받는 패턴입니다.

      비유: 유튜브 구독!
        - 구독 버튼 누르기 = 옵저버 등록 (Subscribe)
        - 새 영상 올리기   = 상태 변화 (Notify)
        - 구독자에게 알림  = 모든 옵저버에게 통보

      여기서는 "기상 관측소"로 보여줍니다.
      날씨가 바뀌면 → 핸드폰 앱, 웹사이트, 전광판 등에 자동 알림!
    ═══════════════════════════════════════════════════════════════════════
    */

    // ┌─────────────────────────────────────────────┐
    // │  인터페이스: IObserver와 ISubject             │
    // └─────────────────────────────────────────────┘

    // 날씨 데이터를 담는 구조체
    public struct WeatherData
    {
        public double Temperature;  // 온도 (°C)
        public double Humidity;     // 습도 (%)
        public double Pressure;     // 기압 (hPa)

        public WeatherData(double temp, double humidity, double pressure)
        {
            Temperature = temp;
            Humidity = humidity;
            Pressure = pressure;
        }
    }

    // IObserver: "알림을 받는 쪽"의 규칙
    // 비유: "구독자는 새 영상이 올라오면 Update()를 실행한다"
    public interface IWeatherObserver
    {
        string Name { get; }
        void Update(WeatherData data);
    }

    // ISubject: "알림을 보내는 쪽"의 규칙
    // 비유: "유튜버는 구독자를 등록/해제/통보 할 수 있다"
    public interface IWeatherSubject
    {
        void Subscribe(IWeatherObserver observer);
        void Unsubscribe(IWeatherObserver observer);
        void NotifyAll();
    }

    // ┌─────────────────────────────────────────────┐
    // │  Subject: 기상 관측소 (알림을 보내는 쪽)      │
    // └─────────────────────────────────────────────┘

    public class WeatherStation : IWeatherSubject
    {
        // 구독자 목록 (옵저버들)
        private readonly List<IWeatherObserver> _observers = new List<IWeatherObserver>();
        private WeatherData _currentData;

        public void Subscribe(IWeatherObserver observer)
        {
            if (!_observers.Contains(observer))
            {
                _observers.Add(observer);
                Console.WriteLine($"  [관측소] {observer.Name} 구독 등록!");
            }
        }

        public void Unsubscribe(IWeatherObserver observer)
        {
            if (_observers.Remove(observer))
            {
                Console.WriteLine($"  [관측소] {observer.Name} 구독 해제!");
            }
        }

        public void NotifyAll()
        {
            Console.WriteLine($"  [관측소] {_observers.Count}개 구독자에게 알림 전송 중...");
            foreach (var observer in _observers)
            {
                observer.Update(_currentData);
            }
        }

        // 날씨가 변하면 자동으로 모든 구독자에게 알립니다
        public void SetWeather(double temp, double humidity, double pressure)
        {
            Console.WriteLine();
            Console.WriteLine($"  ☁ 날씨 변경: {temp}°C, 습도 {humidity}%, 기압 {pressure}hPa");
            _currentData = new WeatherData(temp, humidity, pressure);
            NotifyAll();
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  Observer들: 알림을 받는 여러 구독자들         │
    // └─────────────────────────────────────────────┘

    // 1) 핸드폰 앱 — 온도만 표시
    public class PhoneDisplay : IWeatherObserver
    {
        public string Name => "핸드폰 앱";

        public void Update(WeatherData data)
        {
            Console.WriteLine($"    [{Name}] 현재 온도: {data.Temperature}°C " +
                GetEmoji(data.Temperature));
        }

        private string GetEmoji(double temp)
        {
            if (temp >= 30) return "(더워요!)";
            if (temp >= 20) return "(좋은 날씨)";
            if (temp >= 10) return "(쌀쌀해요)";
            return "(추워요!)";
        }
    }

    // 2) 웹사이트 — 상세 정보 표시
    public class WebsiteDisplay : IWeatherObserver
    {
        public string Name => "날씨 웹사이트";

        public void Update(WeatherData data)
        {
            Console.WriteLine($"    [{Name}] 온도: {data.Temperature}°C | " +
                $"습도: {data.Humidity}% | 기압: {data.Pressure}hPa");
        }
    }

    // 3) 전광판 — 주의보 표시
    public class AlertBoard : IWeatherObserver
    {
        public string Name => "전광판";
        private readonly double _heatThreshold;
        private readonly double _coldThreshold;

        public AlertBoard(double heatThreshold = 33, double coldThreshold = 0)
        {
            _heatThreshold = heatThreshold;
            _coldThreshold = coldThreshold;
        }

        public void Update(WeatherData data)
        {
            if (data.Temperature >= _heatThreshold)
            {
                Console.WriteLine($"    [{Name}] *** 폭염 주의보! {data.Temperature}°C ***");
            }
            else if (data.Temperature <= _coldThreshold)
            {
                Console.WriteLine($"    [{Name}] *** 한파 주의보! {data.Temperature}°C ***");
            }
            else
            {
                Console.WriteLine($"    [{Name}] 정상 범위입니다.");
            }
        }
    }

    // 4) 통계 수집기 — 최고/최저 기록
    public class StatisticsCollector : IWeatherObserver
    {
        public string Name => "통계 수집기";
        private double _maxTemp = double.MinValue;
        private double _minTemp = double.MaxValue;
        private int _count = 0;
        private double _sumTemp = 0;

        public void Update(WeatherData data)
        {
            _count++;
            _sumTemp += data.Temperature;
            if (data.Temperature > _maxTemp) _maxTemp = data.Temperature;
            if (data.Temperature < _minTemp) _minTemp = data.Temperature;

            Console.WriteLine($"    [{Name}] 측정 {_count}회 | " +
                $"최고: {_maxTemp}°C | 최저: {_minTemp}°C | " +
                $"평균: {_sumTemp / _count:F1}°C");
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  C# 이벤트 버전 — 언어 기본 기능 활용         │
    // └─────────────────────────────────────────────┘
    // C#에는 event 키워드가 있어서 옵저버 패턴을 더 쉽게 쓸 수 있습니다.

    public class SimpleWeatherStation
    {
        // event = 구독자 목록을 자동 관리
        public event Action<WeatherData> OnWeatherChanged;

        public void SetWeather(double temp, double humidity, double pressure)
        {
            var data = new WeatherData(temp, humidity, pressure);
            Console.WriteLine($"  ☁ 날씨 변경: {temp}°C");
            OnWeatherChanged?.Invoke(data);
        }
    }

    // ┌─────────────────────────────────────────────┐
    // │  실행                                        │
    // └─────────────────────────────────────────────┘
    internal class Program
    {
        static void Main()
        {
            Console.WriteLine(new string('=', 60));
            Console.WriteLine("  옵저버 패턴: 기상 관측소");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine();

            Lesson1_BasicObserver();
            Lesson2_DynamicSubscription();
            Lesson3_CSharpEvents();
            Lesson4_Summary();
        }

        static void Lesson1_BasicObserver()
        {
            Console.WriteLine("[레슨 1] 기본 옵저버 — 구독하고 알림 받기");
            Console.WriteLine();

            var station = new WeatherStation();

            // 구독자 등록
            var phone = new PhoneDisplay();
            var website = new WebsiteDisplay();
            var alert = new AlertBoard();
            var stats = new StatisticsCollector();

            station.Subscribe(phone);
            station.Subscribe(website);
            station.Subscribe(alert);
            station.Subscribe(stats);

            // 날씨 변경 → 모든 구독자에게 자동 알림!
            station.SetWeather(25, 60, 1013);
            station.SetWeather(35, 80, 1008);
            station.SetWeather(-2, 40, 1020);
            Console.WriteLine();
        }

        static void Lesson2_DynamicSubscription()
        {
            Console.WriteLine("[레슨 2] 구독 해제 — 더 이상 알림 안 받기");
            Console.WriteLine();

            var station = new WeatherStation();
            var phone = new PhoneDisplay();
            var website = new WebsiteDisplay();

            station.Subscribe(phone);
            station.Subscribe(website);

            station.SetWeather(22, 55, 1015);

            // 핸드폰 앱 구독 해제
            Console.WriteLine();
            station.Unsubscribe(phone);

            // 이제 웹사이트만 알림을 받습니다!
            station.SetWeather(28, 65, 1012);
            Console.WriteLine();
        }

        static void Lesson3_CSharpEvents()
        {
            Console.WriteLine("[레슨 3] C# event — 더 쉬운 옵저버 패턴");
            Console.WriteLine();

            /*
              C#의 event 키워드를 쓰면 옵저버 패턴을
              인터페이스 없이도 쉽게 구현할 수 있습니다.
              += 로 구독, -= 로 해제!
            */

            var station = new SimpleWeatherStation();

            // += 로 구독 (lambda로 간단하게!)
            station.OnWeatherChanged += data =>
                Console.WriteLine($"    [앱] {data.Temperature}°C");

            station.OnWeatherChanged += data =>
                Console.WriteLine($"    [웹] 온도: {data.Temperature}°C, 습도: {data.Humidity}%");

            station.SetWeather(20, 50, 1013);
            Console.WriteLine();
        }

        static void Lesson4_Summary()
        {
            Console.WriteLine("[레슨 4] 정리 — 언제 옵저버 패턴을 쓸까?");
            Console.WriteLine();

            Console.WriteLine("  ┌─────────────────┬──────────────────────────────────┐");
            Console.WriteLine("  │  상황            │  예시                            │");
            Console.WriteLine("  ├─────────────────┼──────────────────────────────────┤");
            Console.WriteLine("  │  이벤트 알림     │  버튼 클릭, 데이터 변경 알림       │");
            Console.WriteLine("  │  1:N 통신        │  1개 소스 → N개 화면 업데이트      │");
            Console.WriteLine("  │  느슨한 결합     │  알림 보내는 쪽이 받는 쪽을 모름    │");
            Console.WriteLine("  │  플러그인        │  나중에 구독자를 추가/제거 가능     │");
            Console.WriteLine("  └─────────────────┴──────────────────────────────────┘");
            Console.WriteLine();
            Console.WriteLine("  핵심: Subject는 Observer가 '누구인지' 모릅니다.");
            Console.WriteLine("        IWeatherObserver 인터페이스만 알면 됩니다.");
            Console.WriteLine("        → 새로운 디스플레이를 추가해도 관측소 코드 변경 불필요!");
            Console.WriteLine();
        }
    }
}
