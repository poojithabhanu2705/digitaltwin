import pytest

from core.services.exceptions import (
    NotFoundError,
    ValidationError,
)

from core.services.features.feature_service import (
    FeatureService,
)


class FakeFeatureRepository:

    def __init__(self):
        self.calls = []

    # ------------------------------------------------------------
    # STATION FEATURES
    # ------------------------------------------------------------

    def get_station_feature_by_id(self, feature_id):
        self.calls.append(
            ("get_station_feature_by_id", feature_id)
        )
        return self.station_feature

    def get_latest_station_feature(self, station_id):
        self.calls.append(
            ("get_latest_station_feature", station_id)
        )
        return self.station_feature

    def get_station_features(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_station_features",
                station_id,
                start_time,
                end_time,
            )
        )
        return self.station_features

    def get_station_features_latest_first(
        self,
        station_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_station_features_latest_first",
                station_id,
                start_time,
                end_time,
            )
        )
        return self.station_features

    def save_station_feature(self, **data):
        self.calls.append(
            ("save_station_feature", data)
        )
        return data

    def bulk_save_station_features(self, features):
        self.calls.append(
            ("bulk_save_station_features", features)
        )
        return features

    # ------------------------------------------------------------
    # VEHICLE FEATURES
    # ------------------------------------------------------------

    def get_vehicle_feature_by_id(self, feature_id):
        self.calls.append(
            ("get_vehicle_feature_by_id", feature_id)
        )
        return self.vehicle_feature

    def get_latest_vehicle_feature(self, vehicle_id):
        self.calls.append(
            ("get_latest_vehicle_feature", vehicle_id)
        )
        return self.vehicle_feature

    def get_vehicle_features(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_vehicle_features",
                vehicle_id,
                start_time,
                end_time,
            )
        )
        return self.vehicle_features

    def get_vehicle_features_latest_first(
        self,
        vehicle_id,
        start_time,
        end_time,
    ):
        self.calls.append(
            (
                "get_vehicle_features_latest_first",
                vehicle_id,
                start_time,
                end_time,
            )
        )
        return self.vehicle_features

    def save_vehicle_feature(self, **data):
        self.calls.append(
            ("save_vehicle_feature", data)
        )
        return data


@pytest.fixture
def repository():
    repo = FakeFeatureRepository()

    repo.station_feature = object()
    repo.vehicle_feature = object()

    repo.station_features = [
        object(),
        object(),
    ]

    repo.vehicle_features = [
        object(),
        object(),
    ]

    return repo


@pytest.fixture
def service(repository):
    return FeatureService(
        feature_repository=repository
    )


# ================================================================
# STATION FEATURES
# ================================================================


def test_get_station_feature(service, repository):
    result = service.get_station_feature(10)

    assert result is repository.station_feature

    assert repository.calls == [
        ("get_station_feature_by_id", 10)
    ]


def test_get_station_feature_missing(repository):
    repository.station_feature = None

    service = FeatureService(
        feature_repository=repository
    )

    with pytest.raises(NotFoundError):
        service.get_station_feature(999)


def test_get_latest_station_feature(
    service,
    repository,
):
    result = service.get_latest_station_feature(5)

    assert result is repository.station_feature

    assert repository.calls == [
        ("get_latest_station_feature", 5)
    ]


def test_get_latest_station_feature_missing(repository):
    repository.station_feature = None

    service = FeatureService(
        feature_repository=repository
    )

    with pytest.raises(NotFoundError):
        service.get_latest_station_feature(5)


def test_get_station_features(
    service,
    repository,
):
    start_time = object()
    end_time = object()

    result = service.get_station_features(
        5,
        start_time,
        end_time,
    )

    assert result is repository.station_features

    assert repository.calls == [
        (
            "get_station_features",
            5,
            start_time,
            end_time,
        )
    ]


def test_get_station_features_latest_first(
    service,
    repository,
):
    start_time = object()
    end_time = object()

    result = service.get_station_features_latest_first(
        5,
        start_time,
        end_time,
    )

    assert result is repository.station_features

    assert repository.calls == [
        (
            "get_station_features_latest_first",
            5,
            start_time,
            end_time,
        )
    ]


def test_save_station_feature(
    service,
    repository,
):
    data = {
        "timestamp": object(),
        "station_id": 5,
        "avg_cycle_time": 10.0,
        "utilization": 0.8,
    }

    result = service.save_station_feature(
        **data
    )

    assert result == data

    assert repository.calls == [
        (
            "save_station_feature",
            data,
        )
    ]


def test_station_feature_requires_timestamp(service):
    with pytest.raises(
        ValidationError,
        match="timestamp",
    ):
        service.save_station_feature(
            station_id=5,
        )


def test_station_feature_requires_station(service):
    with pytest.raises(
        ValidationError,
        match="station",
    ):
        service.save_station_feature(
            timestamp=object(),
        )


def test_station_feature_rejects_negative_value(service):
    with pytest.raises(
        ValidationError,
        match="utilization",
    ):
        service.save_station_feature(
            timestamp=object(),
            station_id=5,
            utilization=-1,
        )


# ================================================================
# VEHICLE FEATURES
# ================================================================


def test_get_vehicle_feature(
    service,
    repository,
):
    result = service.get_vehicle_feature(10)

    assert result is repository.vehicle_feature

    assert repository.calls == [
        ("get_vehicle_feature_by_id", 10)
    ]


def test_get_vehicle_feature_missing(repository):
    repository.vehicle_feature = None

    service = FeatureService(
        feature_repository=repository
    )

    with pytest.raises(NotFoundError):
        service.get_vehicle_feature(999)


def test_get_latest_vehicle_feature(
    service,
    repository,
):
    result = service.get_latest_vehicle_feature(5)

    assert result is repository.vehicle_feature

    assert repository.calls == [
        ("get_latest_vehicle_feature", 5)
    ]


def test_get_latest_vehicle_feature_missing(repository):
    repository.vehicle_feature = None

    service = FeatureService(
        feature_repository=repository
    )

    with pytest.raises(NotFoundError):
        service.get_latest_vehicle_feature(5)


def test_get_vehicle_features(
    service,
    repository,
):
    start_time = object()
    end_time = object()

    result = service.get_vehicle_features(
        5,
        start_time,
        end_time,
    )

    assert result is repository.vehicle_features

    assert repository.calls == [
        (
            "get_vehicle_features",
            5,
            start_time,
            end_time,
        )
    ]


def test_get_vehicle_features_latest_first(
    service,
    repository,
):
    start_time = object()
    end_time = object()

    result = service.get_vehicle_features_latest_first(
        5,
        start_time,
        end_time,
    )

    assert result is repository.vehicle_features

    assert repository.calls == [
        (
            "get_vehicle_features_latest_first",
            5,
            start_time,
            end_time,
        )
    ]


def test_save_vehicle_feature(
    service,
    repository,
):
    data = {
        "timestamp": object(),
        "vehicle_id": 5,
        "variant": "SUV",
        "avg_cycle_time": 20.0,
    }

    result = service.save_vehicle_feature(
        **data
    )

    assert result == data

    assert repository.calls == [
        (
            "save_vehicle_feature",
            data,
        )
    ]


def test_vehicle_feature_requires_timestamp(service):
    with pytest.raises(
        ValidationError,
        match="timestamp",
    ):
        service.save_vehicle_feature(
            vehicle_id=5,
            variant="SUV",
        )


def test_vehicle_feature_requires_vehicle(service):
    with pytest.raises(
        ValidationError,
        match="vehicle",
    ):
        service.save_vehicle_feature(
            timestamp=object(),
            variant="SUV",
        )


def test_vehicle_feature_requires_variant(service):
    with pytest.raises(
        ValidationError,
        match="variant",
    ):
        service.save_vehicle_feature(
            timestamp=object(),
            vehicle_id=5,
        )


def test_vehicle_feature_rejects_negative_value(service):
    with pytest.raises(
        ValidationError,
        match="cumulative_risk",
    ):
        service.save_vehicle_feature(
            timestamp=object(),
            vehicle_id=5,
            variant="SUV",
            cumulative_risk=-1,
        )


# ================================================================
# TIME RANGE VALIDATION
# ================================================================


@pytest.mark.parametrize(
    "method_name",
    [
        "get_station_features",
        "get_station_features_latest_first",
        "get_vehicle_features",
        "get_vehicle_features_latest_first",
    ],
)
def test_feature_history_requires_time_range(
    service,
    method_name,
):
    method = getattr(service, method_name)

    with pytest.raises(
        ValidationError,
        match="Both start_time and end_time",
    ):
        if "station" in method_name:
            method(1, None, None)
        else:
            method(1, None, None)


@pytest.mark.parametrize(
    "method_name",
    [
        "get_station_features",
        "get_station_features_latest_first",
        "get_vehicle_features",
        "get_vehicle_features_latest_first",
    ],
)
def test_feature_history_rejects_invalid_time_range(
    service,
    method_name,
):
    method = getattr(service, method_name)

    with pytest.raises(
        ValidationError,
        match="start_time cannot be later",
    ):
        if "station" in method_name:
            method(1, 20, 10)
        else:
            method(1, 20, 10)


# ================================================================
# BULK STATION FEATURES
# ================================================================


def test_bulk_save_station_features(
    service,
    repository,
):
    features = [
        {
            "timestamp": object(),
            "station_id": 1,
            "utilization": 0.5,
        },
        {
            "timestamp": object(),
            "station_id": 1,
            "utilization": 0.7,
        },
    ]

    result = service.bulk_save_station_features(
        features
    )

    assert result is features

    assert repository.calls == [
        (
            "bulk_save_station_features",
            features,
        )
    ]


def test_bulk_save_station_features_rejects_empty(
    service,
):
    with pytest.raises(
        ValidationError,
        match="batch cannot be empty",
    ):
        service.bulk_save_station_features([])


def test_bulk_save_station_features_validates_each_feature(
    service,
):
    features = [
        {
            "timestamp": object(),
            "station_id": 1,
        },
        {
            "timestamp": object(),
            "station_id": 1,
            "utilization": -1,
        },
    ]

    with pytest.raises(
        ValidationError,
        match="utilization",
    ):
        service.bulk_save_station_features(
            features
        )