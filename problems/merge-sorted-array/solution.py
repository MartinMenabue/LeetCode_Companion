from typing import List, Tuple, Dict, Any

class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """
        nums1[m:] = nums2
        nums1.sort()
        print(nums1)
        

if __name__ == '__main__':
    s = Solution()
    s.merge(nums1=[1, 2, 3, 0, 0, 0], m=3, nums2=[2, 5, 6], n=3)
    s.merge(nums1=[1], m=1, nums2=[], n=0)
    s.merge(nums1=[0], m=0, nums2=[1], n=1)
