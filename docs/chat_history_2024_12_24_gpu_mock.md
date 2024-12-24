# Chat History: GPU Mock Mode and ComfyUI Setup Changes
Date: December 24, 2024

## Summary of Changes

### Main Changes
1. Unified handling of GPU and mock modes in the Docker setup
2. Removed separate CPU mode in favor of consistent GPU numbering
3. Updated S3 sync functionality to use different buckets based on AWS_TEST_MODE
4. Improved log directory handling and service verification

### File Changes

#### 1. docker/scripts/start.sh
- Updated s3_sync function to use test or production bucket based on AWS_TEST_MODE
- Simplified GPU mode handling to use consistent directory structure
- Removed checks for NUM_GPUS=0
- Added logging to show which bucket and config is being used

#### 2. docker/scripts/mgpu
- Removed CPU-specific logic and directory naming
- Simplified setup_gpu function to use consistent directory structure
- Updated log directory creation to happen during setup
- Improved error handling and logging

#### 3. docker/scripts/comfyui
- Updated to handle both test mode and no-GPU scenarios with MOCK_GPU=1
- Added better logging to distinguish between test mode and no-GPU mode
- Removed CPU-specific paths in favor of consistent GPU numbering
- Added TEST_GPUS state tracking
- Improved command building logic

### Environment Variables
- **AWS_TEST_MODE**: Controls which bucket and config to use
- **MOCK_GPU**: Set to 1 in either test mode or when no GPUs are available
- **TEST_GPUS**: Used to indicate test mode specifically
- **NUM_GPUS**: Number of GPUs to use (real or mocked)

### Directory Structure
Now consistently using:
- `comfyui_gpu{N}` for all instances, whether real GPU or mocked
- Removed `comfyui_cpu` directory structure
- Log files always in `comfyui_gpu{N}/logs/output.log`

### Configuration Files
- Production: `config_nodes.json`
- Test: `config_nodes_test.json`

## Debugging Notes
- The script now properly handles both test mode and no-GPU scenarios
- MOCK_GPU=1 is set in two cases:
  1. When TEST_GPUS is set (test mode)
  2. When nvidia-smi is not available (no GPUs)
- Log messages clearly indicate which mode is active
- Directory structure remains consistent regardless of mode

## Future Considerations
1. Monitor performance in both real GPU and mock modes
2. Consider adding more detailed logging for debugging
3. May need to adjust timeouts for different environments
4. Consider adding health checks for the services

## Testing Instructions
1. Test with real GPUs:
   ```bash
   # Should use real GPU mode
   docker run ... NUM_GPUS=2
   ```

2. Test with mock GPUs:
   ```bash
   # Should use mock mode
   docker run ... TEST_GPUS=2
   ```

3. Test with no GPUs:
   ```bash
   # Should automatically use mock mode
   docker run ... NUM_GPUS=1
   ```

## Related Issues
- Resolved issue with log file missing during service verification
- Simplified GPU detection and mock mode handling
- Improved consistency in directory naming and structure
