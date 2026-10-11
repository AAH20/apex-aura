import unittest
from core.shm_ring import ShmRingBuffer


class TestShmRingBuffer(unittest.TestCase):
    def test_write_and_read_lifecycle(self):
        ring = ShmRingBuffer(capacity=16, slot_size=128)
        self.assertEqual(ring.available(), 0)

        success = ring.write(b"HELLO_AURA_6G")
        self.assertTrue(success)
        self.assertEqual(ring.available(), 1)

        data = ring.read()
        self.assertEqual(data, b"HELLO_AURA_6G")
        self.assertEqual(ring.available(), 0)

    def test_buffer_saturation(self):
        ring = ShmRingBuffer(capacity=4, slot_size=64)
        for i in range(4):
            self.assertTrue(ring.write(f"MSG_{i}".encode("utf-8")))

        # 5th write should fail (buffer full)
        self.assertFalse(ring.write(b"OVERFLOW"))


if __name__ == "__main__":
    unittest.main()
