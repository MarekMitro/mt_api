# Photoneo Maintenance Tool – API Reference & Procedure Flowchart

---

## API Reference

---

### `MaintenanceTool()`

Create the Python wrapper and load the native MaintenanceTool library.

- **Input:** `PHOXI_CONTROL_PATH` environment variable
- **Output:** `MaintenanceTool` instance (named `mt` below). Raises `PhoXiError` if library cannot be loaded.

---

### `mt.get_maintenance_tool_api_version()`

Read the loaded MaintenanceTool API version.

- **Input:** —
- **Output:** Tuple `(major, minor, patch)`

---

### `mt.check_phoxi_control_compatibility()`

Check whether the installed PhoXi Control is compatible with the MaintenanceTool API.

- **Input:** —
- **Output:** `Bool` — `True` if compatible, `False` otherwise.

---

### `mt.connect(...)`

Connect to a PhoXi device and create an active maintenance session.

- **Input:**
  - `serial_number: str`
  - `output_directory_path: str | None`
  - `validation_target_path: str | None`
  - `store_praw_files: bool`
- **Output:** `MaintenanceToolDevice` handle (named `device` below). Raises `PhoXiError` on connection failure.

---

### `device.disconnect()`

Disconnect the active device session.

- **Input:** —
- **Output:** `None`. Raises `PhoXiError` if no device is connected.

---

### `device.adjust_power()`

Adjust laser power and LED intensity for suitable exposure.

- **Input:** —
- **Output:** `None`. Raises `PhoXiError` if adjustment fails.

---

### `device.trigger()`

Acquire one calibration scan at the current robot pose.

- **Input:** —
- **Output:** `TriggerResult`
  - `.count_of_recognized_marker_points: int`
  - `.count_of_acquired_scans: int`

---

### `device.analyze()`

Analyze acquired scans and determine whether a correction patch can be prepared.

- **Input:** —
- **Output:** `Float` — area / coverage occupancy score. Raises `PhoXiError` if criteria are not fulfilled.

---

### `device.patch()`

Apply the prepared correction patch to the device.

- **Input:** —
- **Output:** `None`. Raises `PhoXiError` if patch was not prepared or patching fails.

---

### `device.restore()`

Restore the device to factory calibration.

- **Input:** —
- **Output:** `None`. Raises `PhoXiError` if restore fails.

---

## Calibration Procedure Flowchart

![Maintenance Tool Flowchart](MT_flowchart.png)
